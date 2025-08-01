import sys
import time
import random
from typing import List, Dict, Set
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import QTimer


class FinishedController:
    def __init__(self, view, username, game_session_id=None):
        self.view = view
        self.username = username
        self.game_session_id = game_session_id

        self.player_scores = {name: 0 for name in self.view.player_names}
        self.current_word = ""
        self.is_winner = False

        self.auto_return_timer = QTimer()
        self.auto_return_timer.setSingleShot(True)

        self._close_callback = None

        if self.view:
            self.connect_view_signals()

    def connect_view_signals(self):
        self.auto_return_timer.timeout.connect(self.return_to_main_menu)
        self.view.set_close_button_listener(self.return_to_main_menu)

    def set_players(self, players):
        self.view.player_names = players
        self.player_scores = {name: 0 for name in players}
        self.view.update_player_scores()

    def update_player_score(self, player_name, score):
        if player_name in self.player_scores:
            self.player_scores[player_name] = score
            self.view.set_player_score(player_name, score)
            self.view.update_player_scores_with_highlight()

    def set_result_message(self, message, is_winner):
        self.is_winner = is_winner
        self.view.set_result_message(message, is_winner)

    def set_word(self, word):
        self.current_word = word
        self.view.set_word_display(word)

    def set_close_callback(self, callback):
        self._close_callback = callback

    def return_to_main_menu(self):
        self.auto_return_timer.stop()
        if self._close_callback:
            self._close_callback()
        self.view.dispose()

    def populate_view_with_data(self):
        if not self.player_scores:
            return

        highest_score = max(self.player_scores.values())
        winners = [name for name, score in self.player_scores.items() if score == highest_score]
        is_tie = len(winners) > 1
        is_actual_winner = self.username in winners if self.username else False

        if is_tie:
            msg = f"It's a tie! Everyone wins with {highest_score} points!"
        elif is_actual_winner:
            msg = f"Victory! You won with the highest score of {highest_score}!"
        else:
            msg = f"Game Over! Player {winners[0]} won with a score of {highest_score}!"

        self.set_result_message(msg, is_actual_winner or is_tie)
        self.auto_return_timer.start(5000)


class GameController:
    def __init__(self, username: str, game_session_id: str, players: List[str],
                 game_service=None, word_service=None):
        """
        Initialize the GameController with enhanced word selection handling.

        Args:
            username: Current player's username
            game_session_id: Identifier for the game session
            players: List of player usernames
            game_service: Optional CORBA GameService client
            word_service: Optional CORBA WordService client
        """
        self.username = username
        self.game_session_id = game_session_id
        self.players = players

        # External services
        self.game_service = game_service
        self.word_service = word_service

        # Game configuration
        self.max_guesses_per_round = 5
        self.round_transition_seconds = 10
        self.max_init_attempts = 5
        self.max_word_retry_attempts = 20  # Increased from default
        self.default_words = [
            "PYTHON", "PROGRAM", "HANGMAN", "DEVELOP", "KEYBOARD",
            "MONITOR", "COMPUTE", "SOFTWARE", "ALGORITHM", "FUNCTION",
            "VARIABLE", "MODULE", "PACKAGE", "LIBRARY", "INTERFACE",
            "ABSTRACT", "INHERIT", "POLYMORPH", "ENCAPSULATION"
        ]  # Extended default word list

        # Game state
        self.init_attempts = 0
        self.current_round = 1
        self.guesses_left = self.max_guesses_per_round
        self.guessed_letters: Set[str] = set()
        self.correct_letters: Set[str] = set()
        self.used_words: Set[str] = set()
        self.player_rounds_won: Dict[str, int] = {player: 0 for player in players}
        self.current_word = ""
        self.masked_word = ""
        self.round_active = False
        self.round_start_time = 0
        self.round_duration_seconds = 30

        # Initialize view
        from meowstery.python_client.player.view.game_view import GameView
        self.view = GameView(players)
        self.setup_view_handlers()

        # Timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game_timer)
        self.init_retry_timer = QTimer()
        self.init_retry_timer.setSingleShot(True)
        self.init_retry_timer.timeout.connect(self.initialize_game_with_retry)

        # FinishedController will be created when needed
        self.finished_controller = None

    def setup_view_handlers(self):
        """Connect view events to controller methods."""
        self.view.set_letter_button_listener(self.handle_letter_guess)

    def start_game(self):
        """Begin the game session with validation."""
        if not (2 <= len(self.players) <= 5):
            self.view.show_overlay_message("Lobby must have 2-5 players")
            QTimer.singleShot(2000, self.navigate_to_main_menu)
            return

        self.view.show()
        self.view.show_overlay_message("Initializing game...")
        self.start_game_timer()
        QTimer.singleShot(500, self.initialize_game_with_retry)

    def initialize_game_with_retry(self):
        """Attempt to initialize round with retry logic."""
        if self.init_retry_timer.isActive():
            self.init_retry_timer.stop()

        if self.initialize_round():
            self.init_attempts = 0
            return

        self.init_attempts += 1
        if self.init_attempts < self.max_init_attempts:
            delay = int(1000 * (1.5 ** self.init_attempts))  # Exponential backoff
            self.view.show_overlay_message(f"Waiting for game data... (Attempt {self.init_attempts})")
            self.init_retry_timer.start(delay)
        else:
            self.handle_initialization_failure()

    def handle_initialization_failure(self):
        """Handle when game initialization fails completely."""
        self.view.show_overlay_message("Failed to initialize game")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Initialization Failed")
        msg.setText("Could not initialize the game.")
        msg.setInformativeText("Would you like to return to main menu?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.buttonClicked.connect(
            lambda btn: self.navigate_to_main_menu() if btn.text().upper().startswith("Y") else None
        )
        msg.exec_()

    def initialize_round(self) -> bool:
        """Initialize a new round with improved word selection handling."""
        try:
            self.fetch_game_settings()
            self.round_start_time = time.time()
            self.round_active = True
            self.guessed_letters.clear()
            self.correct_letters.clear()
            self.guesses_left = self.max_guesses_per_round

            # Get word with fallback mechanisms
            word = self.get_round_word()
            if not word:
                self.view.show_overlay_message("No more words available. Game cannot continue.")
                QTimer.singleShot(4000, self.navigate_to_main_menu)
                return False

            self.current_word = word.upper()
            self.masked_word = "_" * len(self.current_word)

            # Update view
            self.view.set_word_length(len(self.current_word))
            self.view.update_word_display(self.masked_word)
            self.view.update_lives(self.guesses_left)
            self.view.update_round(self.current_round)
            self.view.update_timer(self.round_duration_seconds)
            self.view.reset_keyboard()

            self.view.hide_overlay()
            self.view.show_overlay_message("New round started! Guess the word!")
            QTimer.singleShot(1500, self.view.hide_overlay)

            return True
        except Exception as e:
            print(f"Error initializing round: {str(e)}")
            return False

    def get_round_word(self) -> str:
        """
        Select a word for the current round using the CORBA service first,
        with a fallback to the default word list.
        """
        word = ""
        if self.word_service:
            word = self.get_word_from_service()

        if not word:
            word = self.get_word_from_defaults()

        return word

    def get_word_from_service(self) -> str:
        """
        Attempt to get a unique word from the CORBA service.

        Returns:
            str: New, unused word from the service or empty string
        """
        tried_words = set()

        for attempt in range(self.max_word_retry_attempts):
            try:
                word = self.word_service.getRandomWord(self.game_session_id)
                if not word:
                    continue

                word = word.upper().strip()

                if not word.isalpha():
                    continue

                if word in self.used_words or word in tried_words:
                    tried_words.add(word)
                    print(f"Word '{word}' already used or tried, retrying... ({attempt + 1})")
                    continue

                return word

            except Exception as e:
                print(f"Error getting word from service: {str(e)}")
                break

        print("Failed to get a unique word from the service after max attempts.")
        return ""

    def get_word_from_defaults(self) -> str:
        """
        Select an unused word from the default list.

        Returns:
            str: New unused default word or empty string if exhausted
        """
        unused_defaults = [w for w in self.default_words if w not in self.used_words]
        if not unused_defaults:
            return ""
        return random.choice(unused_defaults)

    def fetch_game_settings(self):
        """Fetch game settings from service or use defaults."""
        # Example: fetch max guesses or round duration from game_service if available
        if self.game_service:
            try:
                settings = self.game_service.getGameSettings(self.game_session_id)
                self.max_guesses_per_round = settings.get('max_guesses', self.max_guesses_per_round)
                self.round_duration_seconds = settings.get('round_duration', self.round_duration_seconds)
            except Exception:
                pass  # fallback to defaults

    def update_game_timer(self):
        """Update the countdown timer during a round."""
        elapsed = int(time.time() - self.round_start_time)
        remaining = self.round_duration_seconds - elapsed
        if remaining <= 0:
            self.round_active = False
            self.end_round()
        else:
            self.view.update_timer(remaining)

    def handle_letter_guess(self, letter: str):
        """Process a guessed letter."""
        if not self.round_active or letter in self.guessed_letters:
            return

        letter = letter.upper()
        self.guessed_letters.add(letter)

        if letter in self.current_word:
            self.correct_letters.add(letter)
            self.update_masked_word()

            if self.is_word_guessed():
                self.player_rounds_won[self.username] += 1
                self.round_active = False
                self.show_round_result(won=True)
        else:
            self.guesses_left -= 1
            self.view.update_lives(self.guesses_left)
            if self.guesses_left <= 0:
                self.round_active = False
                self.show_round_result(won=False)

        self.view.disable_letter_button(letter)
        self.view.update_word_display(self.masked_word)

    def update_masked_word(self):
        """Reveal guessed letters in the masked word."""
        self.masked_word = "".join(
            (c if c in self.correct_letters else "_") for c in self.current_word
        )

    def is_word_guessed(self) -> bool:
        """Check if the player has guessed all letters."""
        return all(letter in self.correct_letters for letter in set(self.current_word))

    def show_round_result(self, won: bool):
        """Display result and prepare for next round or finish."""
        if won:
            msg = f"Congratulations! You guessed the word '{self.current_word}'."
        else:
            msg = f"Round over! The word was '{self.current_word}'."

        self.view.show_overlay_message(msg)

        # Track used word
        self.used_words.add(self.current_word)

        # If max rounds reached, finish game; else next round
        max_rounds = 5
        if self.current_round >= max_rounds:
            self.finish_game()
        else:
            self.current_round += 1
            QTimer.singleShot(self.round_transition_seconds * 1000, self.initialize_game_with_retry)

    def finish_game(self):
        """End the game session and show final scores."""
        self.view.hide()
        if not self.finished_controller:
            from meowstery.python_client.player.view.finished_view import FinishedView
            finished_view = FinishedView(self.players)
            self.finished_controller = FinishedController(finished_view, self.username, self.game_session_id)
            self.finished_controller.set_close_callback(self.navigate_to_main_menu)

        # Set player scores and show winner message
        self.finished_controller.set_players(self.players)
        for player, score in self.player_rounds_won.items():
            self.finished_controller.update_player_score(player, score)

        self.finished_controller.populate_view_with_data()
        self.finished_controller.view.show()

    def navigate_to_main_menu(self):
        """Return user to main menu."""
        self.view.close()
