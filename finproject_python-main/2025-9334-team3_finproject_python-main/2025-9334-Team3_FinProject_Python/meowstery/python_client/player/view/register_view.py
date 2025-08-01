import os
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter, QFrame
from PyQt5.QtGui import QFont, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt


class RegisterPanel(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Meowstery Registration")
        self.setFixedSize(1100, 700)

        # Load Barriecito font
        self.load_barriecito_font()

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(0)

        # Left panel (image)
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet("background-color: #f5f5f5;")

        # Fix: Go up two levels from this file location to get correct res/images path
        base_path = os.path.dirname(os.path.abspath(__file__))
        resource_path = os.path.abspath(os.path.join(base_path, "..", "..", "res", "images"))

        title_path = os.path.join(resource_path, "title.png")
        cat_path = os.path.join(resource_path, "cat5.png")

        title = QLabel()
        title_pixmap = QPixmap(title_path)
        if not title_pixmap.isNull():
            title.setPixmap(title_pixmap.scaledToWidth(500, Qt.SmoothTransformation))
        else:
            print(f"Failed to load image at: {title_path}")
        title.setAlignment(Qt.AlignCenter)

        cat = QLabel()
        cat_pixmap = QPixmap(cat_path)
        if not cat_pixmap.isNull():
            cat.setPixmap(cat_pixmap.scaledToWidth(400, Qt.SmoothTransformation))
        else:
            print(f"Failed to load image at: {cat_path}")
        cat.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(title)
        left_layout.addWidget(cat)

        # Right panel (form)
        right_panel = QFrame()
        form_layout = QVBoxLayout(right_panel)
        form_layout.setContentsMargins(80, 50, 80, 50)

        form_title = QLabel("Create New Account")
        form_title.setFont(QFont(self.barriecito_font.family(), 24, QFont.Bold))
        form_title.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 8px;")
        self.username.setFont(QFont(self.barriecito_font.family(), 14))

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 8px;")
        self.password.setFont(QFont(self.barriecito_font.family(), 14))

        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm Password")
        self.confirm_password.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 8px;")
        self.confirm_password.setFont(QFont(self.barriecito_font.family(), 14))

        self.register_btn = QPushButton("Register")
        self.register_btn.setFixedHeight(40)
        self.register_btn.setStyleSheet("background-color: black; color: white; border-radius: 20px;")
        self.register_btn.setFont(QFont(self.barriecito_font.family(), 16))
        self.register_btn.clicked.connect(self.on_register)

        self.back_btn = QPushButton("Back to Login")
        self.back_btn.setFixedHeight(30)
        self.back_btn.setStyleSheet("color: black; background: none; text-decoration: underline;")
        self.back_btn.setFont(QFont(self.barriecito_font.family(), 12))
        if self.controller:
            self.back_btn.clicked.connect(self.controller.show_login_view)

        form_layout.addWidget(form_title)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.username)
        form_layout.addWidget(self.password)
        form_layout.addWidget(self.confirm_password)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.register_btn)
        form_layout.addStretch()
        form_layout.addWidget(self.back_btn, alignment=Qt.AlignRight)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 500])

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

    def load_barriecito_font(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.abspath(os.path.join(base_path, "..", "..", "res", "Barriecito-Regular.ttf"))
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            self.barriecito_font = QFont("Barriecito")
        else:
            print(f"Warning: Barriecito font not found at {font_path}. Using Arial instead.")
            self.barriecito_font = QFont("Arial")

    def on_register(self):
        user = self.username.text().strip()
        pwd = self.password.text()
        confirm = self.confirm_password.text()
        if pwd != confirm:
            print("Passwords do not match")
            return
        if self.controller:
            self.controller.register(user, pwd)