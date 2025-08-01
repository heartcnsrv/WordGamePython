from datetime import time
from random import random

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from omniORB import CORBA
import CosNaming
from typing import List, Optional

import service
from service import PlayerAccount
from meowstery.python_client.config.config_reader import load_orb_config


def resolve_service(name: str, interface):
    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            host, port = load_orb_config()
            print(f"[CORBA] Attempt {attempt + 1}/{max_retries} to resolve service {name} at {host}:{port}")

            # Add timeout and retry settings
            orb_args = [
                "-ORBInitRef", f"NameService=corbaloc::{host}:{port}/NameService",
                "-ORBclientCallTimeOutPeriod", "10000",  # 10 second timeout
                "-ORBconnectTimeOutPeriod", "10000",  # 10 second connection timeout
                "-ORBretryCount", "3",  # Number of retries for each operation
                "-ORBretryDelay", "1000"  # Delay between retries in milliseconds
            ]

            print(f"[CORBA] Initializing ORB with args: {orb_args}")
            orb = CORBA.ORB_init(orb_args, CORBA.ORB_ID)

            try:
                print("[CORBA] Attempting to resolve NameService...")
                obj = orb.resolve_initial_references("NameService")
                print(f"[CORBA] Successfully resolved NameService")
            except Exception as e:
                print(f"[CORBA] Failed to resolve NameService: {e}")
                print(f"[CORBA] Detailed error: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"[CORBA] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError(
                    f"Could not connect to CORBA naming service at {host}:{port} after {max_retries} attempts. Please check if the server is running and the naming service is started.")

            naming_context = obj._narrow(CosNaming.NamingContext)
            if naming_context is None:
                print("[CORBA] Failed to narrow Naming Service")
                if attempt < max_retries - 1:
                    print(f"[CORBA] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError("Failed to narrow Naming Service")

            service_name = [CosNaming.NameComponent(name, "")]
            try:
                print(f"[CORBA] Attempting to resolve service {name}...")
                resolved_obj = naming_context.resolve(service_name)
                print(f"[CORBA] Successfully resolved service {name}")
            except CosNaming.NamingContext.NotFound as e:
                print(f"[CORBA] Service {name} not found in naming service")
                print(f"[CORBA] Available services: {[str(n) for n in naming_context.list(0)[0]]}")
                if attempt < max_retries - 1:
                    print(f"[CORBA] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError(
                    f"Service {name} not found in naming service after {max_retries} attempts. Please check if the server is running.")
            except Exception as e:
                print(f"[CORBA] Error resolving service {name}: {e}")
                print(f"[CORBA] Detailed error: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"[CORBA] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError(f"Error resolving service {name} after {max_retries} attempts: {e}")

            narrowed = resolved_obj._narrow(interface)
            if narrowed is None:
                print(f"[CORBA] Failed to narrow {name}")
                if attempt < max_retries - 1:
                    print(f"[CORBA] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                raise RuntimeError(f"Failed to narrow {name}")

            print(f"[CORBA] Successfully narrowed service {name}")
            return narrowed

        except Exception as e:
            print(f"[CORBA] Error in resolve_service for {name}: {e}")
            print(f"[CORBA] Detailed error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"[CORBA] Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            raise


class CorbaUserModel:
    def __init__(self):
        self.admin_service = None
        self.login_service = None
        self.leaderboard_service = None
        self.game_manager_service = None
        self.game_service = None
        self.word_service = None

        self._initialize_services()

    def _initialize_services(self):
        try:
            self.admin_service = resolve_service("AdminService", service.AdminService)
            self.login_service = resolve_service("LoginService", service.LoginService)

            try:
                self.leaderboard_service = resolve_service("LeaderboardService", service.LeaderboardService)
            except Exception as e:
                print(f"[CORBA Error] Could not connect to LeaderboardService: {e}")
                self.leaderboard_service = None

            try:
                self.game_manager_service = resolve_service("GameManagerService", service.GameManagerService)
            except Exception as e:
                print(f"[CORBA Error] Could not connect to GameManagerService: {e}")
                self.game_manager_service = None

            try:
                self.game_service = resolve_service("GameService", service.GameService)
            except Exception as e:
                print(f"[CORBA Error] Could not connect to GameService: {e}")
                self.game_service = None

            try:
                self.word_service = resolve_service("WordService", service.WordService)
            except Exception as e:
                print(f"[CORBA Error] Could not connect to WordService: {e}")
                self.word_service = None

        except Exception as e:
            print(f"[CORBA Error] Failed to initialize services: {e}")
            raise RuntimeError(f"Failed to initialize CORBA services: {e}")

    def reset_services(self):
        """Reset all CORBA service connections"""
        print("[CORBA] Resetting all service connections...")
        self._initialize_services()
        print("[CORBA] Service connections reset complete.")

    def register_player(self, username: str, password: str):
        try:
            self.admin_service.createPlayer(username, password)
            return True, "Registration successful"
        except service.AlreadyExists as e:
            return False, f"Username already exists: {e.reason}"
        except Exception as ex:
            return False, f"Error during registration: {ex}"

    def login_player(self, username: str, password: str):
        try:
            login_result = self.login_service.loginPlayer(username, password)
            if login_result.success:
                return True, login_result.sessionId
            else:
                return False, "Login failed"
        except service.InvalidCredentials:
            return False, "Incorrect username or password"
        except service.AlreadyLoggedIn as e:
            return False, f"User already logged in: {e.reason}"
        except Exception as ex:
            return False, f"Error during login: {ex}"

    def logout_player(self, session_id: str):
        try:
            self.login_service.logoutPlayer(session_id)
            return True, "Logout successful"
        except Exception as ex:
            return False, f"Error during logout: {ex}"

    def verify_player_credentials(self, username: str, password: str):
        try:
            login_result = self.login_service.loginPlayer(username, password)
            if login_result.success:
                return True, login_result.sessionId
            return False, None
        except service.InvalidCredentials:
            return False, None
        except Exception as ex:
            raise RuntimeError(f"Error during login: {ex}")

    def get_top_players(self, limit=5) -> List[PlayerAccount]:
        if not self.leaderboard_service:
            return []
        try:
            corba_players = self.leaderboard_service.getTopPlayers()
            # Create new PlayerAccount instances properly
            result = []
            for p in corba_players[:limit]:
                player = PlayerAccount()
                player.username = p.username
                player.wins = p.wins
                result.append(player)
            return result
        except Exception as e:
            print(f"[CORBA Error] Failed to fetch top players: {e}")
            return []


class LobbyModel(QObject):
    game_started = pyqtSignal()
    username_changed = pyqtSignal(str)
    game_session_id_changed = pyqtSignal(str)
    waiting_changed = pyqtSignal(bool)
    status_changed = pyqtSignal(str)
    players_changed = pyqtSignal(list)
    message_changed = pyqtSignal(str)

    def __init__(self, username: Optional[str] = None):
        super().__init__()
        self._username = username
        self._game_session_id = None
        self._is_waiting = False
        self._status = "WAITING"
        self._players = []
        self._message = "Waiting for players..."
        self._game_started_emitted = False

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if value != self._username:
            self._username = value
            self.username_changed.emit(value)

    @property
    def game_session_id(self):
        return self._game_session_id

    @game_session_id.setter
    def game_session_id(self, value):
        if value != self._game_session_id:
            self._game_session_id = value
            self.game_session_id_changed.emit(value)

    @property
    def is_waiting(self):
        return self._is_waiting

    @is_waiting.setter
    def is_waiting(self, value):
        if value != self._is_waiting:
            self._is_waiting = value
            self.waiting_changed.emit(value)

    @property
    def status(self):
        return self._status

    def set_status(self, status: str):
        if status != self._status:
            self._status = status
            self.status_changed.emit(status)

    @property
    def players(self):
        return self._players

    def set_players(self, players: List[str]):
        if players != self._players:
            self._players = players
            self.players_changed.emit(players)

    @property
    def message(self):
        return self._message

    def set_message(self, message: str):
        if message != self._message:
            self._message = message
            self.message_changed.emit(message)

    def join_lobby(self, session_id: str):
        self.game_session_id = session_id
        self.is_waiting = True
        self.set_status("WAITING")
        self.set_message("Waiting for players...")
        return True

    def leave_lobby(self):
        self.game_session_id = None
        self.is_waiting = False
        self.set_status("LEFT")
        self.set_message("Left the lobby.")
        self.set_players([])

    def fetch_lobby_status(self):
        # Suppose you get the current session from the server somewhere:
        current_session = self.get_current_session_from_server()
        if current_session:
            player_count = len(current_session.playerUsernames)
            print(f"Players in lobby: {player_count}, players: {current_session.playerUsernames}")

            if player_count >= 2 and not self._game_started_emitted:
                self._game_started_emitted = True
                self.game_started.emit()
            elif player_count < 2:
                # Reset flag if less than 2 players to allow future start signal
                self._game_started_emitted = False


class LeaderboardModel(QObject):
    leaderboard_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.top_players = []

        try:
            self.leaderboard_service = resolve_service("LeaderboardService", service.LeaderboardService)
        except Exception as e:
            print(f"[LeaderboardModel] Error resolving LeaderboardService: {e}")
            self.leaderboard_service = None

    def get_top_players(self, limit=10):
        if not self.leaderboard_service:
            return
        try:
            players = self.leaderboard_service.getTopPlayers(limit)
            self.top_players = []
            for p in players:
                player = PlayerAccount()
                player.username = p.username
                player.wins = p.wins
                self.top_players.append(player)
            self.leaderboard_changed.emit(self.top_players)
        except Exception as e:
            print(f"[LeaderboardModel] Error fetching leaderboard: {e}")


class GameModel(QObject):
    word_mask_updated = pyqtSignal(str)
    lives_changed = pyqtSignal(int)
    score_changed = pyqtSignal(str, int)
    round_changed = pyqtSignal(int)
    time_changed = pyqtSignal(int)
    game_over = pyqtSignal(str)  # winner or message
    error_occurred = pyqtSignal(str)

    def __init__(self, players, max_lives=5, round_duration=30):
        super().__init__()
        self.players = players
        self.max_lives = max_lives
        self.round_duration = round_duration

        self.reset_game()

    def reset_game(self):
        self.current_round = 1
        self.lives = self.max_lives
        self.current_word = ""
        self.word_mask = ""
        self.guessed_letters = set()
        self.player_scores = {p: 0 for p in self.players}
        self.used_words = set()
        self.round_start_time = None
        self.round_active = False

    def set_new_word(self, word):
        self.current_word = word.upper()
        self.word_mask = "_" * len(word)
        self.guessed_letters.clear()
        self.lives = self.max_lives
        self.round_start_time = time.time()
        self.round_active = True
        self.word_mask_updated.emit(self.word_mask)
        self.lives_changed.emit(self.lives)
        self.round_changed.emit(self.current_round)

    def guess_letter(self, letter):
        letter = letter.upper()
        if not self.round_active:
            self.error_occurred.emit("Round not active.")
            return False

        if letter in self.guessed_letters:
            self.error_occurred.emit(f"Letter '{letter}' already guessed.")
            return False

        self.guessed_letters.add(letter)

        if letter in self.current_word:
            new_mask = list(self.word_mask)
            for idx, ch in enumerate(self.current_word):
                if ch == letter:
                    new_mask[idx] = letter
            self.word_mask = "".join(new_mask)
            self.word_mask_updated.emit(self.word_mask)
            return True
        else:
            self.lives -= 1
            self.lives_changed.emit(self.lives)
            return False

    def check_win(self):
        if self.word_mask == self.current_word:
            # Add +1 point to all players (adjust if needed)
            for p in self.players:
                self.player_scores[p] += 1
                self.score_changed.emit(p, self.player_scores[p])
            self.round_active = False
            return True
        return False

    def check_loss(self):
        if self.lives <= 0:
            self.round_active = False
            return True
        return False

    def time_left(self):
        if not self.round_active or not self.round_start_time:
            return 0
        elapsed = time.time() - self.round_start_time
        return max(0, int(self.round_duration - elapsed))

    def increment_round(self):
        self.current_round += 1
        self.round_changed.emit(self.current_round)

    def get_scores(self):
        return self.player_scores.copy()

    def get_lives(self):
        return self.lives

    def get_word_mask(self):
        return self.word_mask

    def is_round_active(self):
        return self.round_active

    def start_game(self):
        self.update_status.emit("Joining game...")
        try:
            self.game_service.requestToJoinGame(self.username)
        except service.NoOpponentFound as e:
            self.update_status.emit(f"Waiting for opponent: {e.reason}")
            # Optionally retry after a delay
            QTimer.singleShot(2000, self.start_game)
            return
        except Exception as e:
            self.show_error_dialog.emit("CORBA Error", str(e))
            return
        self.init_attempts = 0
        self._initialize_round_with_retry()
        self.state_poll_timer.start(self.POLL_INTERVAL_MS)

    def get_total_rounds(self):
        # Since getTotalRounds is not available in IDL, use local tracking
        try:
            return self.current_round
        except Exception as e:
            print(f"[GameController] Error getting total rounds: {e}")
            return self.current_round

    def get_player_wins(self, username):
        # Since getPlayerRoundWins is not available in IDL, use local tracking
        try:
            # Use local tracking since server method is not available
            return self.player_rounds_won.get(username, 0)
        except Exception as e:
            print(f"[GameController] Error getting wins for {username}: {e}")
            return self.player_rounds_won.get(username, 0)

    def get_current_winner(self):
        # Since getWinnerUsername is not available in IDL, use local winner detection
        try:
            # Determine winner locally based on player wins
            max_wins = -1
            winner = None
            for user, wins in self.player_rounds_won.items():
                if wins > max_wins:
                    max_wins = wins
                    winner = user
            return winner
        except Exception as e:
            print(f"[GameController] Error getting current winner: {e}")
            return None