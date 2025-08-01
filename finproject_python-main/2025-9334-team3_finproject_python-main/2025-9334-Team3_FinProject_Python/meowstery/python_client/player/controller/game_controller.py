from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time
from typing import Optional, Set, Dict, List
from datetime import datetime
import random
import service


class GameController(QObject):
    # Signals (keep existing signal connections)
    update_status = pyqtSignal(str)
    update_word_display = pyqtSignal(str)
    update_guessed_letters = pyqtSignal(set)
    update_guesses_left = pyqtSignal(int)
    update_time_left = pyqtSignal(int)
    update_scores = pyqtSignal(dict)
    disable_keyboard = pyqtSignal()
    enable_keyboard = pyqtSignal()
    show_round_results = pyqtSignal(bool, str)
    start_round = pyqtSignal(int, int)
    disable_letter_button = pyqtSignal(str, bool)
    show_error_dialog = pyqtSignal(str, str)
    navigate_to_main_menu = pyqtSignal()
    game_ended = pyqtSignal(str, dict, str, bool)

    # Constants
    MAX_INIT_ATTEMPTS = 5
    MAX_GUESSES_PER_ROUND = 5
    ROUND_TRANSITION_SECONDS = 10
    POLL_INTERVAL_MS = 1000

    def __init__(self, username: str, game_session_id: str, view: Optional[QObject] = None, corba_services=None):
        super().__init__()
        self.username = username
        self.game_session_id = game_session_id
        self.view = view
        self.corba_services = corba_services
        self.game_service = corba_services.game_service if corba_services else None
        self.word_service = corba_services.word_service if corba_services else None

        # Game state
        self.current_masked_word = ""
        self.guessed_letters = set()
        self.guesses_left = self.MAX_GUESSES_PER_ROUND
        self.round_active = False
        self.game_over = False
        self.is_winner = False
        self.leaderboard_win_updated = False
        self.is_initializing_round = False
        self.round_transition_in_progress = False
        self.current_round = 1
        self.needs_new_word_for_next_round = False
        self.used_words = set()
        self.correct_letters = set()
        self.player_rounds_won = {}

        # Initialization attempts counter
        self.init_attempts = 0

        # Timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self._on_game_timer_tick)
        self.init_retry_timer = QTimer()
        self.init_retry_timer.setSingleShot(True)
        self.init_retry_timer.timeout.connect(self._initialize_round_with_retry)
        self.state_poll_timer = QTimer()
        self.state_poll_timer.timeout.connect(self._poll_game_state)
        self.round_sync_timer = None
        self.game_finished_sync_timer = None

        # Game configuration
        self.round_duration_seconds = 30
        self.round_start_time = None

        if self.view:
            self._connect_view_signals()

    def _connect_view_signals(self):
        """Connect signals to view methods while preserving existing connections"""
        self.update_status.connect(self.view.show_overlay_message)
        self.update_word_display.connect(self.view.word_display_panel.update_word_display)
        self.update_guesses_left.connect(self.view.lives_indicator_panel.update_lives)
        self.update_time_left.connect(self.view.round_info_panel.update_timer)

        # Safe connections for optional methods
        if hasattr(self.view, 'disable_keyboard'):
            self.disable_keyboard.connect(self.view.disable_keyboard)
        if hasattr(self.view, 'enable_keyboard'):
            self.enable_keyboard.connect(self.view.enable_keyboard)
        if hasattr(self.view, 'show_round_results'):
            self.show_round_results.connect(self.view.show_round_results)
        if hasattr(self.view, 'start_round'):
            self.start_round.connect(self.view.start_round)
        if hasattr(self.view, 'disable_letter_button'):
            self.disable_letter_button.connect(self.view.disable_letter_button)
        if hasattr(self.view, 'show_error_dialog'):
            self.show_error_dialog.connect(self.view.show_error_dialog)
        if hasattr(self.view, 'set_letter_button_listener'):
            self.view.set_letter_button_listener(self.handle_letter_guess)
        elif hasattr(self.view, 'keyboard_panel') and hasattr(self.view.keyboard_panel, 'set_letter_button_listener'):
            self.view.keyboard_panel.set_letter_button_listener(self.handle_letter_guess)
        if hasattr(self.view, 'back_clicked'):
            self.view.back_clicked.connect(self.return_to_main_menu)
        # Connect guessed letters update to UI
        if hasattr(self.view, 'update_guessed_letters_display'):
            self.update_guessed_letters.connect(self.view.update_guessed_letters_display)

    def start_game(self):
        print("[GameController] Starting game initialization...")
        self.update_status.emit("Initializing game...")

        # Fetch game configuration
        try:
            self.wait_time_in_seconds = self.corba_services.admin_service.getWaitTime()
            self.round_time_in_seconds = self.corba_services.admin_service.getRoundTime()
            print(
                f"[GameController] Fetched game config: wait={self.wait_time_in_seconds}s, round={self.round_time_in_seconds}s")
        except Exception as e:
            print(f"[GameController] Error fetching game configuration: {e}")
            self.update_status.emit("Error fetching game configuration.")
            return

        # Initialize player rounds won from server
        players = self._get_players_in_session(self.game_session_id) or [self.username]
        for player in players:
            self.player_rounds_won[player] = 0
        self._update_all_player_scores_from_db()  # Get initial scores from server

        # Start game state synchronization
        self._start_game_state_sync()

        # Start game initialization with retry
        self._initialize_round_with_retry()

    def _get_players_in_session(self, game_session_id):
        try:
            game_manager_service = self.corba_services.game_manager_service
            sessions = game_manager_service.listActiveGameSessions()
            for session in sessions:
                if session.gameId == game_session_id:
                    return session.playerUsernames
        except Exception as e:
            print(f"[GameController] Error getting players in session: {e}")
        return None

    def _initialize_round_with_retry(self):
        print(f"[GameController] Attempting to join game (attempt {self.init_attempts + 1})...")
        self.init_attempts += 1

        try:
            game_manager_service = self.corba_services.game_manager_service
            sessions = game_manager_service.listActiveGameSessions()
            current_session = next((s for s in sessions if s.gameId == self.game_session_id), None)

            if not current_session:
                print("[GameController] Session not found during join retry. Returning to lobby.")
                self.update_status.emit("Session not found. Returning to lobby.")
                self.return_to_main_menu()
                return

            if current_session.sessionStatus == "PLAYING" and self.username in current_session.playerUsernames:
                print("[GameController] Session already PLAYING and player present. Starting round polling...")
                self._start_round_polling()
                return
            elif current_session.sessionStatus == "WAITING":
                # Check if we've exceeded the wait time
                if self.init_attempts * self.POLL_INTERVAL_MS > self.wait_time_in_seconds * 1000:
                    print("[GameController] Wait time exceeded. Returning to lobby.")
                    self.update_status.emit("Game start timeout. Returning to lobby.")
                    self.return_to_main_menu()
                    return

                try:
                    self.corba_services.game_service.requestToJoinGame(self.username)
                    print("[GameController] Successfully requested to join game. Starting lobby polling...")
                    self._start_lobby_polling()
                except service.NoOpponentFound as e:
                    print(f"[GameController] No opponent found: {e.reason}. Transitioning to lobby polling...")
                    if self.init_attempts < self.MAX_INIT_ATTEMPTS:
                        self._start_lobby_polling()
                    else:
                        self.update_status.emit("Matchmaking timed out. No opponent found.")
                        self.return_to_main_menu()
            else:
                print(f"[GameController] Session in unexpected state: {current_session.sessionStatus}. Retrying...")
                if self.init_attempts < self.MAX_INIT_ATTEMPTS:
                    self.init_retry_timer.start(self.POLL_INTERVAL_MS)
                else:
                    self.update_status.emit("Matchmaking timed out. Unexpected session state.")
                    self.return_to_main_menu()

        except service.NoOpponentFound as e:
            print(f"[GameController] No opponent found: {e.reason}. Transitioning to lobby polling...")
            if self.init_attempts < self.MAX_INIT_ATTEMPTS:
                self._start_lobby_polling()
            else:
                self.update_status.emit("Matchmaking timed out. No opponent found.")
                self.return_to_main_menu()
        except Exception as e:
            print(f"[GameController] Error during initial join attempt: {e}")
            self.update_status.emit(f"Error during game initialization: {e}")
            self.return_to_main_menu()

    def _start_lobby_polling(self):
        print("[GameController] Starting lobby polling...")
        if not hasattr(self, 'lobby_poll_timer') or not self.lobby_poll_timer.isActive():
            self.lobby_poll_timer = QTimer()
            self.lobby_poll_timer.timeout.connect(self._poll_lobby_state)
            self.lobby_poll_timer.start(self.POLL_INTERVAL_MS)
        self._poll_attempts = 0
        self._max_poll_attempts = (self.wait_time_in_seconds * 1000 // self.POLL_INTERVAL_MS) + 5

    def _poll_lobby_state(self):
        try:
            game_manager_service = self.corba_services.game_manager_service
            sessions = game_manager_service.listActiveGameSessions()
            current_session = next((s for s in sessions if s.gameId == self.game_session_id), None)

            if not current_session:
                print("[GameController] Session not found. Returning to lobby.")
                self.update_status.emit("Session not found. Returning to lobby.")
                self.lobby_poll_timer.stop()
                self.navigate_to_main_menu.emit()
                return

            print(
                f"[LobbyController] Session status: {current_session.sessionStatus}, Players: {current_session.playerUsernames}")

            # Calculate remaining time
            remaining_time = self.wait_time_in_seconds - (self._poll_attempts * self.POLL_INTERVAL_MS / 1000)
            remaining_time = max(0, int(remaining_time))

            self.update_status.emit(
                f"Waiting for game to start... Players: {len(current_session.playerUsernames)}/{current_session.sessionStatus} - Time left: {remaining_time}s")

            if current_session.sessionStatus == "PLAYING":
                print("[GameController] Game is starting!")
                self.update_status.emit("Game is starting!")
                self.lobby_poll_timer.stop()
                self._start_round_polling()
                return

            self._poll_attempts += 1
            if self._poll_attempts > self._max_poll_attempts:
                self.update_status.emit("Matchmaking timed out. Please try again.")
                self.lobby_poll_timer.stop()
                self.navigate_to_main_menu.emit()

        except Exception as e:
            print(f"[GameController] Error polling lobby state: {e}")
            self.update_status.emit(f"Error polling lobby: {e}")
            self.lobby_poll_timer.stop()
            self.navigate_to_main_menu.emit()

    def _start_round_polling(self):
        # Prevent multiple simultaneous round polling starts
        if hasattr(self, '_round_poll_timer') and self._round_poll_timer and self._round_poll_timer.isActive():
            print("[GameController] Round polling already active, skipping...")
            return

        print("[GameController] Starting round polling...")
        try:
            game_manager_service = self.corba_services.game_manager_service
            sessions = game_manager_service.listActiveGameSessions()
            current_session = next((s for s in sessions if s.gameId == self.game_session_id), None)

            if not current_session:
                print("[GameController] Session not found for round polling. Returning to lobby.")
                self.update_status.emit("Session not found. Returning to lobby.")
                self.navigate_to_main_menu.emit()
                return

            round_start_time = self._parse_server_time(current_session.startTime)
            now = time.time()
            if round_start_time is not None and now < round_start_time:
                seconds_to_wait = int(round_start_time - now)
                print(f"[GameController] Waiting for round to start in {seconds_to_wait} seconds...")
                self.update_status.emit(f"Round starts in {seconds_to_wait} seconds...")
                QTimer.singleShot(max(0, seconds_to_wait * 1000), self._start_word_mask_polling)
            else:
                self._start_word_mask_polling()
        except Exception as e:
            print(f"[GameController] Error in _start_round_polling: {e}")
            self.update_status.emit(f"Error starting round: {e}")
            self.navigate_to_main_menu.emit()

    def _parse_server_time(self, time_str):
        if not time_str:
            return None
        try:
            try:
                dt = datetime.fromisoformat(time_str)
            except Exception:
                try:
                    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
                except Exception:
                    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return dt.timestamp()
        except Exception as e:
            print(f"[GameController] Could not parse server time '{time_str}': {e}")
            return None

    def _start_word_mask_polling(self):
        # Prevent multiple simultaneous word mask polling starts
        if hasattr(self, '_round_poll_timer') and self._round_poll_timer and self._round_poll_timer.isActive():
            print("[GameController] Word mask polling already active, skipping...")
            return

        print("[GameController] Starting word mask polling...")
        try:
            # First try to get the word directly
            try:
                actual_word = self.corba_services.word_service.getRandomWord(self.game_session_id)
                print(f"[GameController] Actual word for this round (assigned): {actual_word}")
                self.current_word = actual_word
            except Exception as e:
                print(f"[GameController] Could not fetch/assign actual word: {e}")

            # Then check game status
            try:
                status = self.corba_services.game_service.getGameStatus(self.username)
                print(f"[GameController] Current game status: {status}")
                if status != "PLAYING":
                    print(f"[GameController] Game not in PLAYING state: {status}")
                    self.update_status.emit(f"Waiting for game to start... (Status: {status})")
            except Exception as e:
                print(f"[GameController] Error getting game status: {e}")

            # Start polling for word mask
            self._round_poll_timer = QTimer()
            self._round_poll_timer.timeout.connect(self._poll_word_mask)
            self._round_poll_attempts = 0
            self._max_round_poll_attempts = (self.round_time_in_seconds * 1000 // self.POLL_INTERVAL_MS) + 5
            self._round_poll_timer.start(self.POLL_INTERVAL_MS)

        except Exception as e:
            print(f"[GameController] Error in _start_word_mask_polling: {e}")
            self.update_status.emit(f"Error starting game: {e}")
            self.return_to_main_menu()

    def _poll_word_mask(self):
        try:
            self._round_poll_attempts += 1
            print(f"[GameController] Polling for word mask, attempt {self._round_poll_attempts}")

            if self._round_poll_attempts > self._max_round_poll_attempts:
                print("[GameController] Max polling attempts reached. Stopping word mask polling.")
                self.update_status.emit("Failed to receive word from server. Please try again later.")
                self._round_poll_timer.stop()
                self.return_to_main_menu()
                return

            try:
                # First check game status
                status = self.corba_services.game_service.getGameStatus(self.username)
                if status != "PLAYING":
                    print(f"[GameController] Game not in PLAYING state: {status}")
                    self.update_status.emit(f"Waiting for game to start... (Status: {status})")
                    return

                # Then try to get word mask
                word_mask_info = self.corba_services.game_service.getWordMask(self.username)
                print(f"[GameController] Received word mask info: {word_mask_info}")

                if word_mask_info and hasattr(word_mask_info, 'maskedWord') and word_mask_info.maskedWord:
                    if word_mask_info.maskedWord == self.current_masked_word:
                        print("[GameController] Received same word mask, continuing to poll...")
                        return

                    self._round_poll_timer.stop()
                    self._start_gameplay(word_mask_info)
                    return
                else:
                    print(f"[GameController] No valid word mask info received")
                    # If we have a current word but no mask, create a masked version
                    if self.current_word:
                        print("[GameController] Creating masked word from current word")
                        masked_word = '_' * len(self.current_word)
                        word_mask_info = type('WordMaskInfo', (), {'maskedWord': masked_word})()
                        self._round_poll_timer.stop()
                        self._start_gameplay(word_mask_info)
                        return

                self.update_status.emit(
                    f"Waiting for game to start... ({self._round_poll_attempts}/{self._max_round_poll_attempts})")

            except service.GameNotFound as e:
                print(f"[GameController] Game not found: {e.reason}")
                self.update_status.emit(f"Game not found: {e.reason}")
                self._round_poll_timer.stop()
                self.return_to_main_menu()
            except service.NoOpponentFound as e:
                print(f"[GameController] No opponent found: {e.reason}")
                self.update_status.emit("Waiting for opponent to join...")
            except Exception as e:
                print(f"[GameController] getWordMask error: {e}")
                self.update_status.emit(f"Error getting word mask: {e}")
                self._round_poll_timer.stop()
                self.return_to_main_menu()
        except Exception as e:
            print(f"[GameController] Error in _poll_word_mask: {e}")
            self.update_status.emit(f"Error in round polling: {e}")
            self._round_poll_timer.stop()
            self.return_to_main_menu()

    def get_current_round_number(self):
        """Get the current round number from server using available IDL methods."""
        try:
            # Try to get round information using getRoundStartTime with current round
            # This will help us determine if we're in a valid round
            round_start_time = self.corba_services.game_service.getRoundStartTime(
                self.game_session_id,
                self.current_round
            )

            # If we get a valid start time, the round exists
            if round_start_time:
                print(f"[GameController] Server confirms round {self.current_round} exists")
                return self.current_round
            else:
                # Try the next round
                next_round = self.current_round + 1
                round_start_time = self.corba_services.game_service.getRoundStartTime(
                    self.game_session_id,
                    next_round
                )
                if round_start_time:
                    print(f"[GameController] Server confirms round {next_round} exists, updating local round")
                    self.current_round = next_round
                    return self.current_round
                else:
                    print(f"[GameController] Using local round {self.current_round} (no server round info available)")
                    return self.current_round

        except Exception as e:
            print(f"[GameController] Error getting round number from server: {e}")
            print(f"[GameController] Using local round {self.current_round}")
            return self.current_round

    def _update_all_player_scores_from_db(self):
        """Update player scores using available IDL methods."""
        try:
            # Get current session information to see player list
            game_manager_service = self.corba_services.game_manager_service
            sessions = game_manager_service.listActiveGameSessions()

            for session in sessions:
                if session.gameId == self.game_session_id:
                    # Update player list from session
                    for player in session.playerUsernames:
                        if player not in self.player_rounds_won:
                            self.player_rounds_won[player] = 0

                    # Since we can't get individual player wins from server,
                    # we'll use local tracking but log that we're doing so
                    for player in self.player_rounds_won:
                        if player in session.playerUsernames:
                            print(f"[GameController] Using local wins for {player}: {self.player_rounds_won[player]}")
                        else:
                            # Remove players no longer in session
                            del self.player_rounds_won[player]

                    # Update UI if view is available
                    if hasattr(self.view, 'get_player_scores_panel'):
                        for player, wins in self.player_rounds_won.items():
                            self.view.get_player_scores_panel().update_score(player, wins)
                    break

        except Exception as e:
            print(f"[GameController] Error in _update_all_player_scores_from_db: {e}")

    def get_player_round_wins(self, username: str) -> int:
        """Get the number of rounds won by a player using local tracking."""
        try:
            # Since getPlayerRoundWins is not available in IDL, use local tracking
            wins = self.player_rounds_won.get(username, 0)
            print(f"[GameController] Using local wins for {username}: {wins}")
            return wins
        except Exception as e:
            print(f"[GameController] Error getting wins for {username}: {e}")
            return self.player_rounds_won.get(username, 0)

    def get_all_player_wins(self) -> Dict[str, int]:
        """Get all player wins using local tracking."""
        try:
            # Since getAllPlayerWins is not available in IDL, use local tracking
            print("[GameController] Using local wins for all players")
            return self.player_rounds_won.copy()
        except Exception as e:
            print(f"[GameController] Error getting all player wins: {e}")
            return self.player_rounds_won.copy()

    def mark_round_guessed(self, username: str):
        """Mark the current round as guessed by a player using local tracking."""
        try:
            # Since markRoundGuessed is not available in IDL, update local tracking
            if username not in self.player_rounds_won:
                self.player_rounds_won[username] = 0
            self.player_rounds_won[username] += 1
            print(f"[GameController] Marked round {self.current_round} guessed by {username} (local tracking)")
        except Exception as e:
            print(f"[GameController] Error marking round guessed: {e}")

    def increment_round(self):
        """Increment the round number locally since incrementGameRound is not available in IDL."""
        try:
            # Since incrementGameRound is not available in IDL, increment locally
            print("[GameController] Incrementing round locally (incrementGameRound not available in IDL)")
            self.current_round += 1
        except Exception as e:
            print(f"[GameController] Error incrementing round: {e}")
            self.current_round += 1  # Fallback to local increment

    def is_round_complete(self, round_number: int) -> bool:
        """Check if a round is complete using local logic since isRoundComplete is not available in IDL."""
        try:
            # Since isRoundComplete is not available in IDL, use local logic
            # A round is complete if someone has won or all players are out of guesses
            game_status = self.corba_services.game_service.getGameStatus(self.username)
            if game_status in ["WON", "LOST", "FINISHED"]:
                return True

            # Check if current round is different (indicating round completion)
            if self.current_round > round_number:
                return True

            print(f"[GameController] Assuming round {round_number} incomplete (isRoundComplete not available in IDL)")
            return False
        except Exception as e:
            print(f"[GameController] Error checking round completion: {e}")
            return False

    def _start_gameplay(self, word_mask_info):
        try:
            actual_word = self.word_service.getRandomWord(self.game_session_id)
            print(f"[GameController] Actual word for this round: {actual_word}")
            self.current_word = actual_word
        except Exception as e:
            print(f"[GameController] Could not fetch actual word: {e}")

        self.update_status.emit("Game started! Guess the word!")

        # Initialize the masked word and guessed letters
        self.current_masked_word = word_mask_info.maskedWord

        # Use guessesLeft from server instead of always resetting to MAX_GUESSES_PER_ROUND
        if hasattr(word_mask_info, 'guessesLeft') and word_mask_info.guessesLeft is not None:
            self.guesses_left = word_mask_info.guessesLeft
            print(f"[GameController] Using guesses left from server: {self.guesses_left}")

            # Workaround: If server sends 0 guesses at the start of a round, reset to maximum
            # This handles cases where the server doesn't properly reset guesses for new rounds
            if self.guesses_left == 0 and not self.guessed_letters:
                print("[GameController] Server sent 0 guesses at round start, resetting to maximum")
                self.guesses_left = self.MAX_GUESSES_PER_ROUND
        else:
            self.guesses_left = self.MAX_GUESSES_PER_ROUND
            print(f"[GameController] No guesses left from server, using default: {self.guesses_left}")

        # Extract guessed letters from the initial masked word
        self.guessed_letters = set()
        for char in self.current_masked_word:
            if char != '_':
                self.guessed_letters.add(char)
        print(f"[GameController] Initial guessed letters: {sorted(self.guessed_letters)}")

        self.round_active = True
        self.round_start_time = time.time()

        # Update UI with initial state
        self.update_word_display.emit(self.current_masked_word)
        self.update_guesses_left.emit(self.guesses_left)
        self.update_guessed_letters.emit(self.guessed_letters)
        self.enable_keyboard.emit()

        if hasattr(self.view, 'hide_overlay'):
            self.view.hide_overlay()
        elif hasattr(self.view, 'overlay_panel'):
            self.view.overlay_panel.hide()

        try:
            if self.game_timer:
                self.game_timer.setInterval(1000)
                self.game_timer.start()
            if self.state_poll_timer:
                self.state_poll_timer.start(self.POLL_INTERVAL_MS)
        except Exception as e:
            print(f"[GameController] Error starting timers: {e}")
            self.return_to_main_menu()

    def _poll_game_state(self):
        try:
            status = self.game_service.getGameStatus(self.username)
            if status != "PLAYING":
                self.round_active = False
                self.game_timer.stop()
                self.state_poll_timer.stop()
                self.update_status.emit(f"Game status: {status}")
                self.disable_keyboard.emit()
                self.game_ended.emit(self.username, {}, self.game_session_id, status == "ENDED")
                return
        except Exception:
            pass

    def _on_game_timer_tick(self):
        try:
            elapsed = int(time.time() - self.round_start_time)
            remaining = self.round_duration_seconds - elapsed
            self.update_time_left.emit(max(0, remaining))
            if remaining <= 0:
                # Prevent multiple time-up triggers
                if self.round_transition_in_progress:
                    return

                self.update_status.emit("Time is up!")
                self.disable_keyboard.emit()
                self.round_active = False

                # Check if word was completed when time ran out
                word_completed = '_' not in self.current_masked_word
                if word_completed:
                    # Word was guessed before time ran out - handle as round win
                    self._handle_round_win()
                else:
                    # Word was not guessed - handle as round loss
                    self._handle_round_loss()
        except Exception as e:
            self.show_error_dialog.emit("CORBA Error", str(e))

    def handle_letter_guess(self, letter):
        if not self.round_active:
            self.update_status.emit("Round not active. Wait for the round to start.")
            return

        letter = letter.upper()
        if letter in self.guessed_letters:
            self.update_status.emit(f"Letter '{letter}' already guessed.")
            return

        try:
            game_id = self.game_session_id
            if not game_id:
                print("[GameController] Invalid game session ID for letter check")
                raise Exception("Invalid game session ID")

            word = None
            try:
                word = self.word_service.getRandomWord(game_id)
                print(f"[GameController] Got word directly from WordService: {word}")
                self.current_word = word
            except Exception as e:
                print(f"[GameController] Error getting word from server: {e}")
                if self.current_word:
                    word = self.current_word
                    print(f"[GameController] Using stored word: {word}")
                else:
                    raise Exception("No valid word available for letter check")

            if not word:
                print("[GameController] No valid word available for letter check")
                raise Exception("No valid word available for letter check")

            positions = [i for i, char in enumerate(word) if char.upper() == letter]
            is_correct_guess = bool(positions)

            print(
                f"[GameController] Letter '{letter}' checked with WordService: {'correct' if is_correct_guess else 'incorrect'}")

            try:
                if self.word_service:
                    game_exists = self._check_game_exists_on_server()

                    if game_exists:
                        try:
                            self.game_service.submitGuess(self.username, letter)
                            if not self._update_word_mask():
                                if is_correct_guess:
                                    self._update_local_word_mask(letter, positions)
                        except service.GameNotFound:
                            if is_correct_guess:
                                self._update_local_word_mask(letter, positions)
                        except Exception as e:
                            print(f"[GameController] Error submitting guess to server: {e}")
                            if is_correct_guess:
                                self._update_local_word_mask(letter, positions)
                    else:
                        if is_correct_guess:
                            self._update_local_word_mask(letter, positions)
                else:
                    if is_correct_guess:
                        self._update_local_word_mask(letter, positions)
            except Exception as e:
                print(f"[GameController] Error checking game existence: {e}")
                if is_correct_guess:
                    self._update_local_word_mask(letter, positions)

            self.guessed_letters.add(letter)
            self.update_guessed_letters.emit(self.guessed_letters)
            if hasattr(self.view, 'update_guessed_letters_display'):
                self.view.update_guessed_letters_display(self.guessed_letters)
            self.disable_letter_button.emit(letter, is_correct_guess)

            if is_correct_guess:
                self.correct_letters.add(letter)
            else:
                self.guesses_left -= 1
                self.update_guesses_left.emit(self.guesses_left)

            # Check if word is completed but don't end round automatically
            self._check_word_completion()

            # Check round status (only ends on guesses exhausted or time out)
            self._check_round_status()

        except Exception as e:
            print(f"[GameController] Error processing guess: {e}")
            self.update_status.emit(f"Error: {e}")

    def _update_local_word_mask(self, letter, positions):
        if not positions:
            return

        current_mask = self.current_masked_word
        if not current_mask:
            return

        new_mask = list(current_mask)
        for position in positions:
            if 0 <= position < len(new_mask):
                new_mask[position] = letter

        self.current_masked_word = ''.join(new_mask)
        self.guessed_letters.add(letter)

        self.update_word_display.emit(self.current_masked_word)
        print(f"[GameController] Updated word mask locally to: {self.current_masked_word}")

    def _check_game_exists_on_server(self):
        try:
            word_mask_info = self.game_service.getWordMask(self.username)
            return word_mask_info and word_mask_info.maskedWord
        except service.GameNotFound:
            return False
        except Exception as e:
            print(f"[GameController] Error checking if game exists: {e}")
            return False

    def _update_word_mask(self):
        try:
            word_mask_info = self._get_word_mask_with_retry()

            if not word_mask_info or not word_mask_info.maskedWord:
                return self._handle_null_word_mask()

            processed_mask = self._process_word_mask(word_mask_info.maskedWord)
            word_mask_info.maskedWord = processed_mask

            self.current_masked_word = word_mask_info.maskedWord
            self.guesses_left = word_mask_info.guessesLeft
            self.update_word_display.emit(self.current_masked_word)
            self.update_guesses_left.emit(self.guesses_left)

            return True
        except service.GameNotFound:
            print("[GameController] Game session not found on server. Using local mode.")
            if not self.current_masked_word:
                QTimer.singleShot(1500, self.return_to_main_menu)
            return False
        except Exception as e:
            print(f"[GameController] Error updating word mask: {e}")
            if not self.current_masked_word:
                self.show_error_dialog.emit("Error", f"Error updating word mask: {e}")
            return False

    def _get_word_mask_with_retry(self):
        word_mask_info = None
        retry_count = 0
        last_exception = None

        while retry_count < 3 and not word_mask_info:
            try:
                word_mask_info = self.game_service.getWordMask(self.username)
                return word_mask_info
            except service.GameNotFound as e:
                last_exception = e
                retry_count += 1
                print(
                    f"[GameController] GameNotFound on attempt {retry_count} of 3. Session ID: {self.game_session_id}")
                if retry_count < 3:
                    time.sleep(0.5 * retry_count)
            except Exception as e:
                raise e

        if last_exception:
            raise last_exception
        return None

    def _handle_null_word_mask(self):
        print("[GameController] Received null word mask from server")
        self.show_error_dialog.emit("Error", "Could not retrieve word data from server. Would you like to try again?")
        return False

    def _process_word_mask(self, original_mask):
        player_specific_mask = []
        for char in original_mask:
            if char == '_':
                player_specific_mask.append('_')
            else:
                if char in self.guessed_letters:
                    player_specific_mask.append(char)
                else:
                    player_specific_mask.append('_')
        return ''.join(player_specific_mask)

    def _check_round_status(self):
        # Prevent checking round status during transitions
        if self.round_transition_in_progress:
            return

        try:
            # Only end round when guesses are exhausted or time runs out
            # Don't end round just because word is completely revealed
            if self.guesses_left <= 0:
                self._handle_round_loss()
            # Note: Word completion is now handled separately and doesn't automatically end the round
            # Players can continue guessing until they run out of guesses or time runs out
        except Exception as e:
            print(f"[GameController] Error checking round status: {e}")
            self.update_status.emit("Error checking game status. Returning to main menu...")
            QTimer.singleShot(1500, self.return_to_main_menu)

    def _handle_round_win(self):
        """Handle the logic when a player wins a round"""
        # Prevent multiple simultaneous round win handling
        if self.round_transition_in_progress:
            print("[GameController] Round transition already in progress, skipping round win handling...")
            return

        # Prevent handling if round is already over
        if not self.round_active:
            print("[GameController] Round already inactive, skipping round win handling...")
            return

        try:
            self._stop_round_sync_polling()
            word = self._get_actual_word()
            self.round_active = False

            # First update server with win using local tracking
            try:
                self.mark_round_guessed(self.username)
                print(f"[GameController] Marked round {self.current_round} guessed by {self.username}")
            except Exception as e:
                print(f"[GameController] Error marking round guessed: {e}")

            # Then update local wins from server to ensure consistency
            self._update_all_player_scores_from_db()

            # Get current wins after update
            current_wins = self.player_rounds_won.get(self.username, 0)
            print(f"[GameController] Current wins for {self.username}: {current_wins}")

            # Mark current word as used if possible
            if hasattr(self.word_service, 'markWordAsUsed') and word:
                try:
                    self.word_service.markWordAsUsed(word, self.game_session_id)
                except Exception as e:
                    print(f"[GameController] Error marking word as used: {e}")

            print(f"[GameController] Round won! Word was: {word}")
            if word:
                self.used_words.add(word)

            self.update_status.emit(f"You guessed the word! Round won! The word was: {word}")

            # Reset UI for next round
            self._reset_ui_for_new_round()

            # Check for game win (first to 3 wins)
            if current_wins >= 3:
                self._end_game_with_winner(self.username)
            else:
                # Handle round increment
                try:
                    server_round = self.get_current_round_number()
                    if server_round <= self.current_round:
                        self.increment_round()
                    else:
                        print(f"[GameController] Server round {server_round} ahead of local {self.current_round}")
                        self.current_round = server_round
                except Exception as e:
                    print(f"[GameController] Error incrementing round: {e}")
                    self.current_round += 1  # Fallback to local increment

                # Prepare for next round
                self._prepare_word_for_next_round()
                self._poll_for_next_round()

        except Exception as e:
            print(f"[GameController] Error handling round win: {e}")
            self.show_error_dialog.emit("Round Error", f"Error handling round win: {str(e)}")

    def _start_game_state_sync(self):
        """Start periodic synchronization of game state with server"""
        if hasattr(self, 'game_state_sync_timer'):
            self.game_state_sync_timer.stop()

        self.game_state_sync_timer = QTimer()
        self.game_state_sync_timer.timeout.connect(self._sync_game_state)
        self.game_state_sync_timer.start(3000)  # Sync every 3 seconds
        print("[GameController] Started game state synchronization")

    def _sync_game_state(self):
        """Synchronize game state with server"""
        if self.game_over:
            return

        try:
            # Sync round number
            server_round = self.get_current_round_number()

            # Sync player wins
            self._update_all_player_scores_from_db()

            # Check if game should be ended
            winner = self._get_first_to_three_winner()
            if winner:
                self._end_game_with_winner(winner)

        except Exception as e:
            print(f"[GameController] Error in game state sync: {e}")

    def _handle_round_loss(self):
        """Handle the logic when a player loses a round"""
        # Prevent multiple simultaneous round loss handling
        if self.round_transition_in_progress:
            print("[GameController] Round transition already in progress, skipping round loss handling...")
            return

        # Prevent handling if round is already over
        if not self.round_active:
            print("[GameController] Round already inactive, skipping round loss handling...")
            return

        try:
            if self._is_game_finished_and_show_popup_if_needed():
                return

            self._stop_round_sync_polling()
            word = self._get_actual_word()
            self.round_active = False

            # Mark current word as used if possible
            if hasattr(self.word_service, 'markWordAsUsed') and word:
                try:
                    self.word_service.markWordAsUsed(word, self.game_session_id)
                except Exception as e:
                    print(f"[GameController] Error marking word as used: {e}")

            print(f"[GameController] Round lost! Word was: {word}")
            if word:
                self.used_words.add(word)

            self.update_status.emit(f"Round lost! Out of guesses. The word was: {word}")

            # Reset UI for next round
            self._reset_ui_for_new_round()

            # Update scores and check for winner
            self._update_all_player_scores_from_db()
            winner = self._get_first_to_three_winner()

            if winner:
                self._end_game_with_winner(winner)
            else:
                # Increment round regardless of whether someone guessed correctly
                try:
                    server_round = self.get_current_round_number()
                    if server_round <= self.current_round:
                        self.increment_round()
                    else:
                        self.current_round = server_round
                except Exception as e:
                    print(f"[GameController] Error incrementing round: {e}")
                    self.current_round += 1  # Fallback to local increment

                # Prepare for next round
                self._prepare_word_for_next_round()
                self._poll_for_next_round()

        except Exception as e:
            print(f"[GameController] Error handling round loss: {e}")
            self.show_error_dialog.emit("Round Error", f"Error handling round loss: {str(e)}")

    def _reset_ui_for_new_round(self):
        """Reset all UI elements for a new round"""
        try:
            # Reset keyboard state
            self.enable_keyboard.emit()
            if hasattr(self.view, 'reset_keyboard'):
                self.view.reset_keyboard()

            # Reset guessed letters
            self.guessed_letters = set()
            self.correct_letters = set()
            self.update_guessed_letters.emit(self.guessed_letters)
            if hasattr(self.view, 'update_guessed_letters_display'):
                self.view.update_guessed_letters_display(self.guessed_letters)

            # Reset guesses
            self.guesses_left = self.MAX_GUESSES_PER_ROUND
            self.update_guesses_left.emit(self.guesses_left)

            # Update round display
            if hasattr(self.view, 'start_round'):
                word_length = len(self.current_word) if hasattr(self, 'current_word') and self.current_word else 0
                self.view.start_round(self.current_round, word_length)

            # Reset timer
            self.round_start_time = time.time()
            self.update_time_left.emit(self.round_duration_seconds)

        except Exception as e:
            print(f"[GameController] Error resetting UI: {e}")

    def _get_actual_word(self):
        try:
            if hasattr(self, 'current_word') and self.current_word:
                print(f"[GameController] getActualWord - Using current word from model: {self.current_word}")
                return self.current_word

            if self.word_service:
                try:
                    game_id = self.game_session_id
                    service_word = self.word_service.getRandomWord(game_id)
                    if service_word:
                        print(f"[GameController] getActualWord - Got from WordService: {service_word}")
                        return service_word
                except Exception as e:
                    print(f"[GameController] Error getting word from WordService: {e}")

            if self.current_masked_word:
                return self.current_masked_word + " (partially revealed)"
            return "Unknown word"
        except Exception as e:
            print(f"[GameController] Error getting actual word: {e}")
            return "Unknown word"

    def _is_round_timed_out(self):
        if not self.round_start_time:
            return False
        elapsed = time.time() - self.round_start_time
        return elapsed >= self.round_duration_seconds

    def _get_first_to_three_winner(self):
        for player, wins in self.player_rounds_won.items():
            if wins >= 3:
                return player
        return None

    def _end_game_with_winner(self, winner_username):
        print(f"[GameController] endGameWithWinner called with winner: {winner_username}")
        try:
            self.game_over = True
            self.is_winner = (winner_username == self.username)

            # Stop all timers
            self._stop_all_timers()

            # Since setGameFinished is not available in IDL, use local game end logic
            print("[GameController] Using local game end logic (setGameFinished not available in IDL)")

            # Update final scores
            self._update_all_player_scores_from_db()

            # Emit game ended signal with final state
            final_scores = self.get_all_player_wins()
            self.game_ended.emit(winner_username, final_scores, "Game completed", self.is_winner)

            # Update leaderboard if available
            try:
                from .leaderboards_controller import LeaderboardsController
                leaderboard_controller = LeaderboardsController(self.corba_services)
                try:
                    leaderboard_controller.update_player_wins(winner_username)
                except AttributeError:
                    print("[GameController] update_player_wins not available in LeaderboardsController")
                self.leaderboard_win_updated = True
            except Exception as e:
                print(f"[GameController] Error updating leaderboard wins via LeaderboardsController: {e}")

        except Exception as e:
            print(f"[GameController] Error in endGameWithWinner: {e}")
            self.show_error_dialog.emit("Game End Error", f"Error ending game: {str(e)}")

    def _is_game_finished_and_show_popup_if_needed(self):
        try:
            game_manager_service = self.corba_services.game_manager_service
            if not game_manager_service:
                return False

            sessions = game_manager_service.listActiveGameSessions()
            for session in sessions:
                if session.gameId == self.game_session_id and session.sessionStatus == "FINISHED":
                    if not self.is_winner:
                        winner_username = None
                        try:
                            # Since getWinnerUsername is not available in IDL, use local winner detection
                            self._update_all_player_scores_from_db()
                            winner_username = self._get_first_to_three_winner()
                            print(f"[GameController] Winner from local detection in popup check: {winner_username}")
                        except Exception as e:
                            print(f"[GameController] Error in winner detection: {e}")

                        if not winner_username:
                            winner_username = "Unknown Player"
                            print("[GameController] Using 'Unknown Player' in popup check")

                        self._end_game_with_winner(winner_username)
                        return True
        except Exception as e:
            print(f"[GameController] Error in isGameFinishedAndShowPopupIfNeeded: {e}")
        return False

    def _start_game_finished_sync_polling(self):
        if self.game_finished_sync_timer:
            self.game_finished_sync_timer.stop()
        self.game_finished_sync_timer = QTimer()
        self.game_finished_sync_timer.timeout.connect(self._poll_game_finished)
        self.game_finished_sync_timer.start(1000)
        print("[GameController] Started game-finished status polling.")

    def _stop_game_finished_sync_polling(self):
        if self.game_finished_sync_timer:
            self.game_finished_sync_timer.stop()
            self.game_finished_sync_timer = None
            print("[GameController] Stopped game-finished status polling.")

    def _poll_game_finished(self):
        if self.game_over:
            return
        try:
            if not self.game_service:
                return

            status = self.game_service.getGameStatus(self.username)
            if status == "WON":
                if not self.is_winner:
                    self.is_winner = True
                    self._stop_game_finished_sync_polling()
                    self._end_game_with_winner(self.username)
            elif status == "LOST":
                self._stop_game_finished_sync_polling()
                winner = None
                try:
                    # Since getWinnerUsername is not available in IDL, use local winner detection
                    self._update_all_player_scores_from_db()
                    winner = self._get_first_to_three_winner()
                    print(f"[GameController] Winner from local detection: {winner}")
                except Exception as e:
                    print(f"[GameController] Error in winner detection: {e}")

                if not winner:
                    winner = "Unknown Player"
                    print("[GameController] Using 'Unknown Player' as winner fallback")

                self._end_game_with_winner(winner)

        except service.GameNotFound:
            self._stop_game_finished_sync_polling()
            fallback_winner = None
            try:
                fallback_winner = self._get_first_to_three_winner()
            except Exception as e:
                print(f"[GameController] Error getting fallback winner: {e}")

            if not fallback_winner:
                fallback_winner = "Unknown Player"

            self._end_game_with_winner(fallback_winner)
        except Exception as e:
            print(f"[GameController] Error in game-finished polling: {e}")

    def _poll_for_next_round(self):
        # Prevent multiple simultaneous next round polling
        if hasattr(self, '_poll_timer') and self._poll_timer and self._poll_timer.isActive():
            print("[GameController] Next round polling already active, skipping...")
            return

        completed_round = self.current_round - 1
        print(f"[GameController] Started polling for completion of round {completed_round}")

        try:
            # Use getRoundStartTime to check if next round exists
            try:
                next_round_start_time = self.corba_services.game_service.getRoundStartTime(
                    self.game_session_id,
                    self.current_round
                )
                print(f"[GameController] Polling for next round. Current round: {self.current_round}")

                if next_round_start_time:
                    print(f"[GameController] Next round {self.current_round} exists on server")
                else:
                    print(f"[GameController] Next round {self.current_round} not yet available on server")

            except Exception as e:
                print(f"[GameController] Error checking round availability: {e}")
                # Fallback to local round increment
                self.current_round += 1
                self._show_round_transition(False, self._get_actual_word(), self._initialize_round)
                return

        except Exception as e:
            print(f"[GameController] Error checking server round number: {e}")
            self.current_round += 1
            self._show_round_transition(False, self._get_actual_word(), self._initialize_round)
            return

        fallback_timer = QTimer()
        fallback_timer.setSingleShot(True)
        fallback_timer.timeout.connect(lambda: self._handle_fallback_timer())
        fallback_timer.start(15000)

        self._poll_timer = QTimer()
        self._poll_timer.timeout.connect(lambda: self._handle_poll_timer(completed_round, fallback_timer))
        self._poll_timer.start(500)

    def _handle_fallback_timer(self):
        if self.game_over:
            return
        print("[GameController] Fallback timer triggered - forcing round transition")
        try:
            # Use getRoundStartTime to check if current round exists
            round_start_time = self.corba_services.game_service.getRoundStartTime(
                self.game_session_id,
                self.current_round
            )
            if not round_start_time:
                # Try next round
                next_round_start_time = self.corba_services.game_service.getRoundStartTime(
                    self.game_session_id,
                    self.current_round + 1
                )
                if next_round_start_time:
                    self.current_round += 1
                    print(f"[GameController] Fallback sync: Updated client round to {self.current_round}")
        except Exception as e:
            print(f"[GameController] Error in fallback sync: {e}")

        if self._is_game_finished_and_show_popup_if_needed():
            return
        self._show_round_transition(False, self._get_actual_word(), self._initialize_round)

    def _handle_poll_timer(self, completed_round, fallback_timer):
        if self.game_over:
            self._poll_timer.stop()
            fallback_timer.stop()
            return
        try:
            # Use is_round_complete method which uses available IDL methods
            round_complete = self.is_round_complete(completed_round)

            # Use getRoundStartTime to check current round availability
            current_round_start_time = self.corba_services.game_service.getRoundStartTime(
                self.game_session_id,
                self.current_round
            )

            print(f"[GameController] Polling - Round {completed_round} complete: {round_complete}, "
                  f"Current round available: {bool(current_round_start_time)}, Client round: {self.current_round}")

            if self._is_game_finished_and_show_popup_if_needed():
                self._poll_timer.stop()
                fallback_timer.stop()
                return

            if round_complete or not current_round_start_time:
                self._poll_timer.stop()
                fallback_timer.stop()

                # Check if next round exists
                next_round_start_time = self.corba_services.game_service.getRoundStartTime(
                    self.game_session_id,
                    self.current_round + 1
                )
                if next_round_start_time:
                    self.current_round += 1
                    print(f"[GameController] Next round {self.current_round} available, advancing")

                print(f"[GameController] Round {completed_round} complete, showing intermission")

                player_won = '_' not in self.current_masked_word
                self._prepare_word_for_next_round()
                self._show_round_transition(player_won, self._get_actual_word(), self._initialize_round)

        except Exception as e:
            print(f"[GameController] Error polling for round completion: {e}")

    def _prepare_word_for_next_round(self):
        game_id = self.game_session_id
        if not self.word_service or not game_id:
            print("[GameController] Cannot prepare word for next round: " +
                  ("WordService is null" if not self.word_service else "Invalid game ID"))
            return None

        try:
            time.sleep(0.1)
            self.needs_new_word_for_next_round = True
            print("[GameController] Marked model to get new word at round start")
            return "WORD_WILL_BE_FETCHED_AT_ROUND_START"
        except Exception as e:
            print(f"[GameController] Error preparing word for next round: {e}")
            return None

    def _initialize_round(self):
        """Initialize a new round with proper UI reset"""
        try:
            # Reset keyboard and UI state
            self.enable_keyboard.emit()
            if hasattr(self.view, 'reset_keyboard'):
                self.view.reset_keyboard()

            # Reset game state for new round
            self.guessed_letters = set()
            self.correct_letters = set()
            self.guesses_left = self.MAX_GUESSES_PER_ROUND

            # Update round number from server or use local
            server_round = self.get_current_round_number()
            if server_round > self.current_round:
                print(f"[GameController] Syncing client round {self.current_round} -> {server_round}")
                self.current_round = server_round

            # Update UI
            self.update_guesses_left.emit(self.guesses_left)
            self.update_guessed_letters.emit(self.guessed_letters)
            if hasattr(self.view, 'start_round'):
                self.view.start_round(self.current_round, len(self.current_word))

            return True
        except Exception as e:
            print(f"[GameController] Error initializing round: {e}")
            return False

    def _show_round_transition(self, won, actual_word, on_transition_complete):
        if self.game_over:
            if hasattr(self.view, 'hide_overlay'):
                self.view.hide_overlay()
            return

        # Prevent multiple simultaneous round transitions
        if self.round_transition_in_progress:
            print("[GameController] Round transition already in progress, skipping...")
            return

        self.round_transition_in_progress = True
        print(f"[GameController] Starting round transition for round {self.current_round}")

        # Reset UI elements during transition
        self.disable_keyboard.emit()
        if hasattr(self.view, 'reset_keyboard'):
            self.view.reset_keyboard()

        # Show transition UI
        self.show_round_results.emit(won, actual_word)

        # Prepare for next round after delay
        def do_transition():
            # --- ADDED: Reset round state for new round ---
            # Confirm with server if next round exists
            next_round_start_time = self.corba_services.game_service.getRoundStartTime(
                self.game_session_id, self.current_round
            )
            if next_round_start_time:
                print(
                    f"[GameController] Confirmed new round {self.current_round} exists on server. Resetting round state.")
                self.guesses_left = self.MAX_GUESSES_PER_ROUND
                self.guessed_letters = set()
                self.correct_letters = set()
                self.update_guesses_left.emit(self.guesses_left)
                self.update_guessed_letters.emit(self.guessed_letters)
                if hasattr(self.view, 'start_round'):
                    word_length = len(self.current_word) if hasattr(self, 'current_word') and self.current_word else 0
                    self.view.start_round(self.current_round, word_length)
            else:
                print(
                    f"[GameController] Next round {self.current_round} not yet available on server. Not resetting round state.")
            # --- END ADDED ---
            self._complete_round_transition(on_transition_complete)

        QTimer.singleShot(self.ROUND_TRANSITION_SECONDS * 1000, do_transition)

    def _complete_round_transition(self, on_transition_complete):
        """Complete the round transition with proper cleanup"""
        try:
            # Reset timer and UI
            self.round_start_time = time.time()
            self.update_time_left.emit(self.round_duration_seconds)

            # Clear overlay
            if hasattr(self.view, 'hide_overlay'):
                self.view.hide_overlay()

            # Execute completion callback
            if on_transition_complete:
                on_transition_complete()

            # Start the new round gameplay after initialization
            self._start_round_polling()

            # Reset transition flag
            self.round_transition_in_progress = False
            print(f"[GameController] Round transition completed for round {self.current_round}")

        except Exception as e:
            print(f"[GameController] Error completing round transition: {e}")
            self.round_transition_in_progress = False

    def _stop_round_sync_polling(self):
        if hasattr(self, 'round_sync_timer') and self.round_sync_timer:
            self.round_sync_timer.stop()
            self.round_sync_timer = None
            print("[GameController] Stopped round sync polling.")

    def return_to_main_menu(self):
        print("[GameController] Navigating to main menu...")
        self._stop_all_timers()
        self.navigate_to_main_menu.emit()

    def _stop_all_timers(self):
        timers = [
            getattr(self, '_round_poll_timer', None),
            getattr(self, 'lobby_poll_timer', None),
            getattr(self, 'init_retry_timer', None),
            getattr(self, 'state_poll_timer', None),
            getattr(self, 'game_timer', None),
            getattr(self, 'round_sync_timer', None),
            getattr(self, 'game_finished_sync_timer', None),
            getattr(self, '_poll_timer', None)
        ]

        for timer in timers:
            if timer and hasattr(timer, 'stop'):
                try:
                    timer.stop()
                except Exception as e:
                    print(f"[GameController] Error stopping timer: {e}")

    def _check_word_completion(self):
        """Check if the word is completely revealed and handle accordingly"""
        if '_' not in self.current_masked_word:
            print("[GameController] Word completely revealed!")
            self.update_status.emit("Word revealed! You can continue guessing or wait for the round to end.")
            # Don't automatically end the round - let it continue until time runs out or guesses exhausted
            return True
        return False

    def end_round_early(self):
        """Allow player to end the round early if word is completed"""
        if not self.round_active:
            return

        if '_' not in self.current_masked_word:
            print("[GameController] Player ending round early - word completed")
            self.update_status.emit("Ending round early - word completed!")
            self._handle_round_win()
        else:
            print("[GameController] Cannot end round early - word not completed")
            self.update_status.emit("Cannot end round early - word not yet completed!")