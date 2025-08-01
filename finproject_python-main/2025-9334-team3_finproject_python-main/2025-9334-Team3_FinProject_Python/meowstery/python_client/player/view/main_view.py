from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont, QCursor, QPainter, QColor, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt, QRect, pyqtSignal
import os


class RoundedButton(QFrame):
    clicked = pyqtSignal()

    def __init__(self, main_text, sub_text, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 60)
        self.radius = 25
        self.bg_color = QColor(0, 0, 0)
        self.fg_color = QColor(255, 255, 255)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        base_path = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.normpath(os.path.join(base_path, "..", "..", "res", "Barriecito-Regular.ttf"))

        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            font_family = "Barriecito"
        else:
            font_family = "SansSerif"

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        main_label = QLabel(main_text)
        main_font = QFont(font_family, 24, QFont.Bold)
        main_label.setFont(main_font)
        main_label.setStyleSheet("color: white;")
        main_label.setAlignment(Qt.AlignCenter)

        sub_label = QLabel(sub_text)
        sub_font = QFont(font_family, 14)
        sub_label.setFont(sub_font)
        sub_label.setStyleSheet("color: white;")
        sub_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(main_label)
        layout.addWidget(sub_label)
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.NoPen)
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, self.radius, self.radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class UserMainView(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Meowstery")
        self.setFixedSize(1096, 612)
        self.setStyleSheet("background-color: white;")

        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.normpath(os.path.join(base_path, "..", "..", "res", "images"))
        font_path = os.path.normpath(os.path.join(base_path, "..", "..", "res", "Barriecito-Regular.ttf"))

        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            self.font_family = "Barriecito"
        else:
            self.font_family = "SansSerif"

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left panel
        left_panel = QWidget()
        left_panel.setFixedSize(700, 600)
        left_panel.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 10, 0, 0)
        left_layout.setSpacing(0)

        title_path = os.path.join(image_path, "title.png")
        title_pixmap = QPixmap(title_path)
        title_label = QLabel()
        if not title_pixmap.isNull():
            scaled_title = title_pixmap.scaledToWidth(400, Qt.SmoothTransformation)
            title_label.setPixmap(scaled_title)
        else:
            title_label.setText("Title Image Missing")
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)

        cat_path = os.path.join(image_path, "cat1.png")
        cat_pixmap = QPixmap(cat_path)
        cat_label = QLabel()
        if not cat_pixmap.isNull():
            scaled_cat = cat_pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cat_label.setPixmap(scaled_cat)
        else:
            cat_label.setText("Cat Image Missing")
        cat_label.setAlignment(Qt.AlignCenter)
        cat_label.setContentsMargins(0, -40, 0, 0)
        left_layout.addWidget(cat_label)

        left_panel.setLayout(left_layout)

        # Right panel
        right_panel = QWidget()
        right_panel.setFixedSize(450, 600)
        right_panel.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(40, 30, 40, 30)
        right_layout.setSpacing(40)

        username_label = QLabel(f"meow, {username}")
        username_font = QFont(self.font_family, 18)
        username_label.setFont(username_font)
        username_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(username_label)
        right_layout.addSpacing(20)

        self.playButton = RoundedButton("Meow !", "Play")
        self.leaderboardsButton = RoundedButton("Meow Meow !", "Leaderboards")
        self.howToPlayButton = RoundedButton("Meow Meow Meow !", "How To Play")
        self.leaveButton = RoundedButton("Meow... :(", "Leave....:(")

        right_layout.addWidget(self.playButton)
        right_layout.addWidget(self.leaderboardsButton)
        right_layout.addWidget(self.howToPlayButton)
        right_layout.addWidget(self.leaveButton)

        right_layout.addStretch()
        right_panel.setLayout(right_layout)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        self.setLayout(main_layout)

        self.username_label = username_label

    def updateWelcomeLabel(self, message):
        if self.username_label:
            self.username_label.setText(message)