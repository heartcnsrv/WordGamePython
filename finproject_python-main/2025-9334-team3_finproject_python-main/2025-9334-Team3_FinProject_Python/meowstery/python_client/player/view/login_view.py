import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QFrame
)
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt, QSize


class ImagePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        self.setStyleSheet("background-color: #f5f5f5;")
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)

        self.catmoon = QLabel()
        self.catmoon.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.catmoon)

        self.load_images()

    def load_images(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        resource_path = os.path.abspath(os.path.join(base_path, "..", "..", "res", "images"))

        title_path = os.path.join(resource_path, "title.png")
        catmoon_path = os.path.join(resource_path, "catmoon.png")

        logo_pixmap = QPixmap(title_path)
        catmoon_pixmap = QPixmap(catmoon_path)

        if not logo_pixmap.isNull():
            self.logo.setPixmap(logo_pixmap.scaledToWidth(600, Qt.SmoothTransformation))
        else:
            print(f"Logo image not found at: {title_path}")

        if not catmoon_pixmap.isNull():
            self.catmoon.setPixmap(catmoon_pixmap.scaledToWidth(450, Qt.SmoothTransformation))
        else:
            print(f"Catmoon image not found at: {catmoon_path}")


class UserLoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meowstery Login")
        self.setFixedSize(1100, 700)
        self.setGeometry(100, 100, 1100, 700)

        # Load custom font
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "res", "Barriecito-Regular.ttf"))
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                self.custom_font = font_families[0]
            else:
                self.custom_font = "Barriecito"
        else:
            print("Custom font not found, using default.")
            self.custom_font = "Barriecito"

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(0)

        # Left Panel: Images
        self.left_panel = ImagePanel()
        splitter.addWidget(self.left_panel)

        # Right Panel: Login form
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 8px;")
        self.username.setFont(QFont(self.custom_font, 14))

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 8px;")
        self.password.setFont(QFont(self.custom_font, 14))

        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedSize(QSize(120, 35))
        self.login_btn.setFont(QFont(self.custom_font, 14))

        self.sign_up_btn = QPushButton("Sign Up")
        self.sign_up_btn.setFixedSize(QSize(120, 35))
        self.sign_up_btn.setFont(QFont(self.custom_font, 14))

        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedSize(QSize(80, 30))
        self.back_btn.setFont(QFont(self.custom_font, 12))

        form_layout = QVBoxLayout()
        form_layout.addWidget(self.username)
        form_layout.addWidget(self.password)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)
        form_layout.addSpacing(20)

        sign_up_label = QLabel("Don't have an account yet?")
        sign_up_label.setFont(QFont(self.custom_font, 12))
        sign_up_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(sign_up_label)
        form_layout.addWidget(self.sign_up_btn, alignment=Qt.AlignCenter)

        right_container = QVBoxLayout()
        right_container.addLayout(form_layout)
        right_container.addStretch()

        back_layout = QHBoxLayout()
        back_layout.addStretch()
        back_layout.addWidget(self.back_btn)

        right_container.addLayout(back_layout)

        right_panel = QFrame()
        right_panel.setLayout(right_container)
        splitter.addWidget(right_panel)

        splitter.setSizes([600, 500])

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def get_username(self):
        return self.username.text().strip()

    def get_password(self):
        return self.password.text()

    def get_login_button(self):
        return self.login_btn

    def get_back_button(self):
        return self.back_btn

    def get_sign_up_button(self):
        return self.sign_up_btn