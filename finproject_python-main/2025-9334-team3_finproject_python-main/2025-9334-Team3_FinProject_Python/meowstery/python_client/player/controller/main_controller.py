from PyQt5.QtWidgets import QMessageBox

from meowstery.python_client.player.model.user_model import LobbyModel, CorbaUserModel
from meowstery.python_client.player.view.lobby_view import LobbyView
from meowstery.python_client.player.view.main_view import UserMainView
from meowstery.python_client.player.controller.lobby_controller import LobbyController
from meowstery.python_client.player.controller.leaderboards_controller import LeaderboardsController
from meowstery.python_client.player.view.howto_view import HowToPlayView

class MainController:
    def __init__(self, username, session_id, orb, naming_context):
        self.username = username
        self.session_id = session_id
        self.orb = orb
        self.naming_context = naming_context

        # Initialize CORBA services
        self.corba_services = CorbaUserModel()

        # Views and Controllers
        self.main_view = UserMainView(username)
        self.howto_view = None
        self.leaderboards_controller = None
        self.lobby_controller = None

        self.attach_handlers()

    def show(self):
        self.main_view.updateWelcomeLabel(f"Welcome, {self.username}!")
        self.main_view.show()

    def attach_handlers(self):
        self.main_view.playButton.clicked.connect(self.handle_play)
        self.main_view.leaderboardsButton.clicked.connect(self.handle_leaderboards)
        self.main_view.howToPlayButton.clicked.connect(self.handle_how_to_play)
        self.main_view.leaveButton.clicked.connect(self.handle_leave)

    def handle_play(self):
        print("[MainController] Play button clicked")
        self.main_view.close()
        self.open_lobby(self.username, self.session_id)

    def open_lobby(self, username, session_id):
        print("[MainController] Opening lobby")

        lobby_model = LobbyModel(username)
        lobby_view = LobbyView()

        self.lobby_controller = LobbyController(lobby_model, lobby_view, self.corba_services)

        # Connect the lobby signal to a handler in MainController
        self.lobby_controller.show_main_menu.connect(self.on_lobby_show_main_menu)

        self.lobby_controller.show_lobby_view()

    def on_lobby_show_main_menu(self):
        print("[MainController] Showing main menu again")
        self.main_view.show()

    def handle_leaderboards(self):
        print("[MainController] Leaderboards button clicked")
        self.show_leaderboards()

    def show_leaderboards(self):
        print("[MainController] Showing leaderboard view")
        self.leaderboards_controller = LeaderboardsController()
        self.leaderboards_controller.show_leaderboards_view()

    def handle_how_to_play(self):
        print("[MainController] How to Play button clicked")
        self.show_howto_play()

    def show_howto_play(self):
        print("[MainController] Showing how to play")
        self.howto_view = HowToPlayView(self.username)
        self.howto_view.show()

    def handle_leave(self):
        reply = QMessageBox.question(
            self.main_view,
            "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            print("[MainController] User confirmed logout")
            self.main_view.close()
            self.return_to_login_view()

    def return_to_login_view(self):
        print("[MainController] Returning to login view")
        from meowstery.python_client.player.controller.login_controller import UserLoginController
        self.login_controller = UserLoginController(self.orb, self.naming_context)
        self.login_controller.show_login()
