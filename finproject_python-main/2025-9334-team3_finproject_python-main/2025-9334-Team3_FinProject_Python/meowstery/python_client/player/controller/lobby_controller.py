import CORBA
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication
import random
import traceback
import time

from meowstery.python_client.player.controller.game_controller import GameController
from meowstery.python_client.player.model.user_model import LobbyModel
from meowstery.python_client.player.view.game_view import GameView
import service


class LobbyController(QObject):
    show_main_menu = pyqtSignal()
    game_started = pyqtSignal()  # signal to notify transition to game controller

    POLL_INTERVAL_MS = 1000  # Poll every 1 second to match Java client
    MAX_RETRY_ATTEMPTS = 5
    MATCHMAKING_TIMEOUT_MS = 30000  # 30 seconds default timeout

    def _reset_transition_flag(self):
        self._game_transitioned = False

    def __init__(self, model: 'LobbyModel', view, corba_services):
        super().__init__()
        self.model = model
        self.view = view
        self.corba = corba_services

        self.game_controller = None
        self._game_transitioned = False
        # Initialize the attribute here
        self._game_transition_started = False

        # Connect buttons if available
        if hasattr(self.view, "main_menu_button") and self.view.main_menu_button is not None:
            self.view.main_menu_button.clicked.connect(self.on_main_menu)
        if hasattr(self.view, "restart_button") and self.view.restart_button is not None:
            self.view.restart_button.clicked.connect(self.on_restart)

        # Timers
        self.matchmaking_timer = QTimer()
        self.matchmaking_timer.setSingleShot(True)
        self.matchmaking_timer.timeout.connect(self.on_matchmaking_timeout)

        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.fetch_lobby_status)

        # Connect model signals to view update methods
        self.model.status_changed.connect(self.view.update_status)
        self.model.players_changed.connect(self.view.update_players_list)
        self.model.message_changed.connect(self.view.update_waiting_message)

        # Connect the game_started signal to handler to navigate to game screen
        self.game_started.connect(self.on_game_started)

        # Start matchmaking immediately
        self.start_waiting()

        # Add new state tracking variables
        self._last_session_status = None
        self._status_change_count = 0
        self._force_transition = False

        self.last_wait_time_from_server = None

    def check_corba_connection(self):
        """Check if CORBA services are available and working"""
        try:
            self.corba.game_manager_service._non_existent()
            return True
        except Exception as e:
            print(f"[LobbyController] CORBA connection check failed: {e}")
            return False

    def reset_corba_services(self):
        """More robust CORBA service reset with proper error handling"""
        try:
            print("[LobbyController] Performing CORBA reset...")
            if hasattr(self.corba, '_orb'):
                try:
                    self.corba._orb.destroy()
                except:
                    pass
                self.corba._orb = None

            import CORBA
            args = ["-ORBgiopMaxMsgSize", "209715200"]
            self.corba._orb = CORBA.ORB_init(args, CORBA.ORB_ID)

            from meowstery.python_client.player.model.user_model import resolve_service
            services = [
                ("AdminService", "admin_service", service.AdminService),
                ("LoginService", "login_service", service.LoginService),
                ("LeaderboardService", "leaderboard_service", service.LeaderboardService),
                ("GameManagerService", "game_manager_service", service.GameManagerService),
                ("GameService", "game_service", service.GameService),
                ("WordService", "word_service", service.WordService)
            ]

            for service_name, attr, service_type in services:
                try:
                    setattr(self.corba, attr, resolve_service(service_name, service_type))
                except Exception as e:
                    print(f"[LobbyController] Failed to resolve {service_name}: {e}")
                    try:
                        setattr(self.corba, attr, resolve_service(service_name, service_type, timeout=5000))
                    except Exception as e2:
                        print(f"[LobbyController] Critical: Could not reconnect to {service_name}")
                        raise ConnectionError(f"Could not reconnect to {service_name}")
            print("[LobbyController] CORBA reset completed.")
            return True
        except Exception as e:
            print(f"[LobbyController] CORBA reset failed: {e}")
            return False

    def start_waiting(self):
        print("[LobbyController] Starting matchmaking...")
        self._reset_transition_flag()
        self.lobby_start_time = time.time()  # Track when the lobby started

        # Start polling for lobby status
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.fetch_lobby_status)
        self.poll_timer.start(1000)

        self._initialize_session()

    def _initialize_session(self):
        try:
            print("[LobbyController] Initializing game session...")
            session_id = self.corba.game_manager_service.joinOrCreateGameSession(self.model.username)
            if not session_id:
                raise Exception("Failed to create or join game session")
            self.model.game_session_id = session_id
            print(f"[LobbyController] Session ID: {self.model.game_session_id}")

            self.wait_time_in_seconds = self.corba.admin_service.getWaitTime()
            self.round_time_in_seconds = self.corba.admin_service.getRoundTime()
            print(f"[LobbyController] Server config - Wait time: {self.wait_time_in_seconds}s, Round time: {self.round_time_in_seconds}s")

            self.lobby_poll_timer = QTimer()
            self.lobby_poll_timer.timeout.connect(self.fetch_lobby_status)
            self.lobby_poll_timer.start(1000)
            print("[LobbyController] Started lobby status polling")
            self.model.set_message(f"Waiting for players... (Timeout in {self.wait_time_in_seconds}s)")

        except Exception as e:
            print(f"[LobbyController] Error initializing session: {e}")
            traceback.print_exc()
            self.model.set_message(f"Error initializing game session: {e}")
            self.on_main_menu()

    def _handle_matchmaking_timeout(self):
        print("[LobbyController] Matchmaking timeout reached")
        self.poll_timer.stop()  # Ensure polling is stopped to prevent multiple game views
        if self._game_transition_started:
            print("[LobbyController] Transition already started, skipping timeout logic.")
            return
        try:
            sessions = self.corba.game_manager_service.listActiveGameSessions()
            current_session = next((s for s in sessions if s.gameId == self.model.game_session_id), None)

            if current_session:
                num_players = len(current_session.playerUsernames)
                print(f"[LobbyController] Players at timeout: {num_players}")

                if current_session.sessionStatus == "PLAYING":
                    if not self._game_transition_started:
                        print("[LobbyController] Session is 'PLAYING' at timeout, starting game.")
                        self._game_transition_started = True
                        self.poll_timer.stop()
                        self.navigate_to_game_screen()
                    else:
                        print("[LobbyController] Game transition already started, skipping.")
                else:
                    # TIMEOUT: Show retry/main menu buttons and stop polling
                    print("[LobbyController] Matchmaking timed out. No match found.")
                    self.view.show_restart_and_main_menu_buttons()
                    if self.view.restart_button:
                        self.view.restart_button.clicked.connect(self.on_restart)
                    if self.view.main_menu_button:
                        self.view.main_menu_button.clicked.connect(self.on_main_menu)
                    self.model.set_status("ERROR")
                    self.model.set_message("Matchmaking timed out. No match found.")
            else:
                print("[LobbyController] Session not found at timeout.")
                self.model.set_message("Session lost. Returning to main menu.")
                self.on_main_menu()
        except Exception as e:
            print(f"[LobbyController] Error during timeout handling: {e}")
            self.model.set_message("Error during timeout handling.")
            self.on_main_menu()

    def fetch_lobby_status(self):
        try:
            # Fetch the latest wait time from the server
            wait_time_from_server = self.corba.admin_service.getWaitTime()

            # If the wait time has changed, reset the timer
            if self.last_wait_time_from_server is None or wait_time_from_server != self.last_wait_time_from_server:
                print(f"[LobbyController] Wait time updated from {self.last_wait_time_from_server} to {wait_time_from_server}, resetting timer.")
                self.lobby_start_time = time.time()
                self.last_wait_time_from_server = wait_time_from_server

            if self._game_transition_started:
                self.poll_timer.stop()
                return

            elapsed = time.time() - self.lobby_start_time
            remaining = max(0, int(wait_time_from_server - elapsed))

            # Update UI with the latest remaining time
            self.model.set_message(f"Waiting for players... (Timeout in {remaining}s)")

            if elapsed >= wait_time_from_server:
                print("[LobbyController] Wait time expired, triggering timeout logic.")
                self.poll_timer.stop()  # Stop polling before handling timeout
                self._handle_matchmaking_timeout()
                return

            # ... rest of your polling logic (check session status, etc.) ...
            sessions = self.corba.game_manager_service.listActiveGameSessions()
            current_session = next((s for s in sessions if s.gameId == self.model.game_session_id), None)
            if current_session:
                if current_session.sessionStatus == "PLAYING" and len(current_session.playerUsernames) >= 2:
                    if not self._game_transition_started:
                        print("[LobbyController] Game is ready, transitioning to game.")
                        self._game_transition_started = True
                        self.poll_timer.stop()
                        self.navigate_to_game_screen()
                    else:
                        print("[LobbyController] Game transition already started, skipping.")
                        self.poll_timer.stop()
                # else: keep waiting, UI already updated above
            else:
                # handle session not found
                print("[LobbyController] Session not found during polling.")
                self.model.set_message("Session lost. Returning to main menu.")
                self.on_main_menu()
        except Exception as e:
            print(f"[LobbyController] Error in fetch_lobby_status: {e}")
            self.model.set_message("Error during lobby polling.")
            self.on_main_menu()

    def _attempt_rejoin(self):
        try:
            print("[LobbyController] Attempting to rejoin session using joinOrCreateGameSession...")
            session_id = self.corba.game_manager_service.joinOrCreateGameSession(self.model.username)
            if session_id:
                print(f"[LobbyController] Successfully rejoined session: {session_id}")
                self.model.game_session_id = session_id
                return True
            else:
                print("[LobbyController] Failed to get session ID from joinOrCreateGameSession")
                return False
        except Exception as e:
            print(f"[LobbyController] Rejoin failed: {e}")
            traceback.print_exc()
            return False

    def _handle_polling_error(self, error):
        if isinstance(error, CORBA.TRANSIENT):
            print("[LobbyController] CORBA transient error - attempting reset")
            try:
                self.reset_corba_services()
                self.fetch_lobby_status()
            except Exception as e:
                print(f"[LobbyController] CORBA reset failed: {e}")
                self.model.set_message("Connection lost")
                self.on_main_menu()
        else:
            print(f"[LobbyController] Non-fatal polling error: {error}")
            self.model.set_message("Temporary connection issue...")

    def on_game_started(self):
        print("[LobbyController] Game started detected. Navigating to game screen...")
        self.navigate_to_game_screen()

    def navigate_to_game_screen(self):
        print("[LobbyController] Starting game transition...")
        try:
            # Fetch current session info
            sessions = self.corba.game_manager_service.listActiveGameSessions()
            current_session = next((s for s in sessions if s.gameId == self.model.game_session_id), None)

            if not current_session:
                print("[LobbyController] Session disappeared - aborting")
                self._game_transition_started = False
                self.model.set_message("Game session ended")
                self.on_main_menu()
                return

            players = current_session.playerUsernames

            # Instantiate your GameView
            self._game_view = GameView(players)

            # Instantiate your GameController with the game view and other needed info
            self._game_controller = GameController(
                self.model.username,
                self.model.game_session_id,
                self._game_view,
                self.corba
            )

            # Connect signals from game controller to handle main menu transition post-game
            self._game_controller.navigate_to_main_menu.connect(self.on_main_menu)

            # Show the game view and start the game
            self._game_view.show()
            self._game_controller.start_game()

            # Close the lobby view
            self.view.close()
            print("[LobbyController] Game transition complete")
        except Exception as e:
            print(f"[LobbyController] Transition failed: {e}")
            import traceback
            traceback.print_exc()
            # Cleanup in case of failure
            if hasattr(self, '_game_view'):
                self._game_view.close()
            self._game_transition_started = False
            # Do NOT restart the polling timer here if the session is already PLAYING
            self.model.set_message("Failed to start game - try again")

    def on_matchmaking_timeout(self, force_timeout=False):
        print("[LobbyController] Matchmaking timed out.")
        self.poll_timer.stop()
        self.view.show_restart_and_main_menu_buttons()
        # Reconnect signals (if buttons newly shown)
        if self.view.restart_button:
            self.view.restart_button.clicked.connect(self.on_restart)
        if self.view.main_menu_button:
            self.view.main_menu_button.clicked.connect(self.on_main_menu)
        self.model.set_status("ERROR")
        if force_timeout:
            self.model.set_message("Matchmaking timed out. No meow found.")
        else:
            # Only show timeout if there is only 1 player
            sessions = self.corba.game_manager_service.listActiveGameSessions()
            current_session = next((s for s in sessions if s.gameId == self.model.game_session_id), None)
            if current_session and len(current_session.playerUsernames) > 1:
                print("[LobbyController] Enough players after timeout, keep polling.")
                self.poll_timer.start(self.POLL_INTERVAL_MS)
                return
            self.model.set_message("Matchmaking timed out. No meow found.")

    def handle_matchmaking_error(self, e):
        print(f"[LobbyController] Matchmaking error: {e}")
        self.poll_timer.stop()

        self.view.show_restart_and_main_menu_buttons()

        if self.view.restart_button:
            self.view.restart_button.clicked.connect(self.on_restart)
        if self.view.main_menu_button:
            self.view.main_menu_button.clicked.connect(self.on_main_menu)

        self.model.set_status("ERROR")
        self.model.set_message(f"Error: {str(e)}")

    def on_restart(self):
        print("[LobbyController] Restart clicked, restarting matchmaking.")
        self._reset_transition_flag()

        # Stop all timers first
        self.poll_timer.stop()

        # Reset CORBA before starting again
        if not self.reset_corba_services():
            print("[LobbyController] Failed to reset CORBA services, returning to main menu")
            self.on_main_menu()
            return

        # Wait a moment for CORBA to stabilize
        QTimer.singleShot(1000, self.start_waiting)

    def on_main_menu(self):
        print("[LobbyController] Going back to main menu")
        self._reset_transition_flag()

        # Clean up CORBA
        if hasattr(self.corba, '_orb'):
            try:
                self.corba._orb.destroy()
            except:
                pass
            self.corba._orb = None

        self.view.close()
        self.show_main_menu.emit()

    def show_lobby_view(self):
        self.view.show()

    def _sanitize_username(self, username):
        """More lenient username sanitization that preserves most characters"""
        if not username:
            return f"player{random.randint(1000, 9999)}"

        # Allow common special characters but remove problematic ones
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
        sanitized = ''.join(c for c in username if c in allowed_chars)

        if not sanitized:
            sanitized = f"player{random.randint(1000, 9999)}"
        elif len(sanitized) > 20:  # Prevent overly long usernames
            sanitized = sanitized[:20]

        return sanitized

    def start_game_polling(self, game_manager_service):
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(lambda: self.check_game_start(game_manager_service))
        self._poll_timer.start(2000)  # Poll every 2 seconds

    def stop_game_polling(self):
        if hasattr(self, '_poll_timer'):
            self._poll_timer.stop()

    def check_game_start(self, game_manager_service):
        if not self.model.game_session_id:
            return
        try:
            has_started = game_manager_service.hasGameStarted(self.model.game_session_id)
            if has_started:
                self.stop_game_polling()
                self.model.set_status("STARTED")
                self.model.set_message("Game has started!")
                self.model.is_waiting = False
        except Exception as e:
            print(f"[LobbyModel] Error checking game start: {e}")
