from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
import sys

from meowstery.python_client.player.view.register_view import RegisterPanel

class UserRegisterController(QObject):
    show_login_signal = pyqtSignal()
    registration_success = pyqtSignal(str)

    def __init__(self, model=None, view=None):
        super().__init__()
        self.model = model
        self.view = view

        if self.view:
            self.connect_view_signals()

    def connect_view_signals(self):
        self.view.register_btn.clicked.connect(self.on_register_clicked)
        self.view.back_btn.clicked.connect(self.handle_back)

    def on_register_clicked(self):
        username = self.view.username.text().strip()
        password = self.view.password.text()
        confirm_password = self.view.confirm_password.text()

        if password != confirm_password:
            QMessageBox.critical(self.view, "Registration Error", "Passwords do not match")
            return

        self.register(username, password)

    def show_register(self):
        if self.view:
            self.view.show()

    def handle_back(self):
        if self.view:
            self.view.close()
        self.show_login_signal.emit()

    def register(self, username, password):
        if not self.validate_input(username, password, password):
            return

        try:
            if not self.model:
                raise RuntimeError("No model provided for registration")

            success, message = self.model.register_player(username, password)

            if success:
                QMessageBox.information(self.view, "Registration Complete", "Registration successful! You can now log in.")
                self.registration_success.emit(username)
                self.handle_back()
            else:
                QMessageBox.critical(self.view, "Registration Error", message or "Registration failed. Please try again.")
        except Exception as ex:
            QMessageBox.critical(self.view, "Registration Error", f"Registration failed: {str(ex)}")
            print(f"Registration error: {ex}", file=sys.stderr)

    def validate_input(self, username, password, confirm_password):
        if len(username) < 3:
            QMessageBox.critical(self.view, "Registration Error", "Username must be at least 3 characters long")
            return False

        if len(password) < 3:
            QMessageBox.critical(self.view, "Registration Error", "Password must be at least 3 characters long")
            return False

        if password != confirm_password:
            QMessageBox.critical(self.view, "Registration Error", "Passwords do not match")
            return False

        return True

    def cleanup(self):
        if self.view:
            self.view.close()