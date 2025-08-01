from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QCursor, QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt
import sys
import os

import CORBA
import CosNaming

from meowstery.python_client.player.controller.login_controller import UserLoginController


class MeowsteryClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeowsteryClient")
        self.setFixedSize(500, 450)
        self.setStyleSheet("background-color: white;")
        self.orb = None
        self.naming_context = None

        self.load_barriecito_font()
        self.init_ui()

    def load_barriecito_font(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.abspath(os.path.join(base_path, "..", "res", "Barriecito-Regular.ttf"))
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            self.barriecito_font = QFont("Barriecito")
        else:
            print(f"Warning: Barriecito font not found at {font_path}. Using Arial instead.")
            self.barriecito_font = QFont("Arial")

    def get_image_path(self, filename):
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "..", "res", "images", filename)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.title_image = QLabel()

        pixmap = QPixmap(self.get_image_path("title.png"))
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
            self.title_image.setPixmap(pixmap)
            self.title_image.setAlignment(Qt.AlignCenter)
        else:
            print("Main window title image not found.")

        layout.addWidget(self.title_image, alignment=Qt.AlignCenter)

        ip_layout = QHBoxLayout()
        ip_label = QLabel("Server IP:")
        ip_label.setFont(QFont(self.barriecito_font.family(), 16))
        ip_label.setStyleSheet("color: black;")
        ip_layout.addWidget(ip_label)

        self.ip_field = QLineEdit()
        self.ip_field.setFixedHeight(40)
        self.ip_field.setFont(QFont(self.barriecito_font.family(), 14))
        self.ip_field.setStyleSheet("""
            border: 2px solid black;
            padding-left: 10px;
            padding-right: 10px;
            color: black;
        """)
        ip_layout.addWidget(self.ip_field)
        layout.addLayout(ip_layout)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.connect_button.setFixedHeight(45)
        self.connect_button.setFont(QFont(self.barriecito_font.family(), 18, QFont.Bold))
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #323232;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        self.connect_button.clicked.connect(self.on_connect_clicked)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def on_connect_clicked(self):
        ip = self.ip_field.text().strip()
        if not ip:
            QMessageBox.warning(self, "Input Error", "Please enter a server IP.")
            return

        try:
            orb_args = ["-ORBInitRef", f"NameService=corbaloc::{ip}:1050/NameService"]
            self.orb = CORBA.ORB_init(orb_args)

            obj = self.orb.resolve_initial_references("NameService")
            self.naming_context = obj._narrow(CosNaming.NamingContext)
            if self.naming_context is None:
                raise RuntimeError("Failed to narrow the root naming context")

            QMessageBox.information(self, "Connected", f"Successfully connected to NameService at {ip}")

            self.open_user_login()

        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", f"Failed to connect to {ip}:\n{str(e)}")

    def open_user_login(self):
        self.close()

        self.login_controller = UserLoginController(orb=self.orb, naming_context=self.naming_context)
        self.login_controller.show_login()


def main():
    app = QApplication(sys.argv)
    client = MeowsteryClient()
    client.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
