from PyQt5.QtWidgets import QMessageBox
from meowstery.python_client.player.view.login_view import UserLoginView
from meowstery.python_client.player.controller.main_controller import MainController
from meowstery.python_client.player.controller.register_controller import UserRegisterController
from meowstery.python_client.player.model.user_model import CorbaUserModel


class UserLoginController:
    last_session_id = None

    def __init__(self, orb, naming_context):
        self.orb = orb
        self.naming_context = naming_context
        self.login_view = UserLoginView()
        self.model = CorbaUserModel()  # Uses CORBA under the hood
        self.attach_handlers()



    def show_login(self):
        self.login_view.show()

    def attach_handlers(self):
        self.login_view.get_login_button().clicked.connect(self.perform_login)
        self.login_view.get_back_button().clicked.connect(self.handle_back)
        self.login_view.get_sign_up_button().clicked.connect(self.handle_sign_up)

    def handle_back(self):
        from meowstery.python_client.player.main import MeowsteryClient
        self.login_view.close()
        self.main_window = MeowsteryClient()
        self.main_window.show()

    def handle_sign_up(self):
        self.login_view.close()

        from meowstery.python_client.player.view.register_view import RegisterPanel
        from meowstery.python_client.player.model.user_model import CorbaUserModel
        from meowstery.python_client.player.controller.register_controller import UserRegisterController

        register_view = RegisterPanel()
        register_model = CorbaUserModel()

        self.register_controller = UserRegisterController(register_model, register_view)

        # Connect signal to show login view when user presses back on register
        self.register_controller.show_login_signal.connect(self.show_login_from_register)

        # Connect registration success signal if you want to handle that too
        self.register_controller.registration_success.connect(self.handle_registration_success)

        self.register_controller.show_register()

    def show_login_from_register(self):
        # This method is called when register view emits show_login_signal
        if hasattr(self, 'register_controller') and self.register_controller.view:
            self.register_controller.view.close()
        self.show_login()

    def show_register(self):
        self.login_view.close()
        self.register_controller.show_register()

    def handle_registration_success(self, username):
        QMessageBox.information(self.login_view, "Registration Successful",
                                f"User '{username}' registered successfully! Please log in.")
        self.show_login_from_register()

    def perform_login(self):
        username = self.login_view.get_username()
        password = self.login_view.get_password()

        if not username or not password:
            QMessageBox.warning(self.login_view, "Login Error", "Please enter both username and password.")
            return

        try:
            success, session_or_msg = self.model.verify_player_credentials(username, password)
            if success:
                UserLoginController.last_session_id = session_or_msg
                QMessageBox.information(self.login_view, "Login Successful", "Welcome back!")
                self.login_view.close()

                from meowstery.python_client.player.controller.main_controller import MainController

                self.main_controller = MainController(username, session_or_msg, self.orb, self.naming_context)
                self.main_controller.show()

            else:
                msg = session_or_msg if session_or_msg else "Invalid username or password."
                QMessageBox.critical(self.login_view, "Login Failed", msg)
        except Exception as ex:
            QMessageBox.critical(self.login_view, "Login Error", f"An error occurred:\n{str(ex)}")