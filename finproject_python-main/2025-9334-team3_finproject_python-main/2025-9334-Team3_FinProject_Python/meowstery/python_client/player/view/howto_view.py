import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QPushButton, QFrame
)
from PyQt5.QtGui import (
    QFontDatabase, QFont, QPainter, QColor, QPixmap, QCursor, QBrush, QLinearGradient
)
from PyQt5.QtCore import Qt
from future.moves import sys


class RoundedPanel(QFrame):
    def __init__(self, radius=30, bg_color=QColor(50, 50, 50), parent=None):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.NoPen)
        rect = self.rect()
        painter.drawRoundedRect(rect, self.radius, self.radius)
        super().paintEvent(event)


class RoundedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.radius = 25
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFont(QFont("Barriecito", 32))
        self.setStyleSheet("color: white;")
        self.bg_color = QColor(50, 50, 50)
        self.setMinimumSize(300, 80)
        self.setMaximumSize(300, 80)
        self.setFlat(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.bg_color.darker(130))
        gradient.setColorAt(1, self.bg_color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

        painter.setPen(QColor('white'))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


class HowToPlayView(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("How To Meow")
        self.setFixedSize(1600, 1000)
        self.setStyleSheet("background-color: rgb(255,255,255);")
        self.accent_color = QColor(50, 50, 50)

        self.load_barriecito_font()
        self.init_ui()

    def load_barriecito_font(self):
        # Go two levels up from current file directory, then into res/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "res"))
        font_path = os.path.join(base_path, "Barriecito-Regular.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            self.barriecito_font = QFont("Barriecito")
        else:
            print(f"Warning: Font not found at {font_path}. Using Arial instead.")
            self.barriecito_font = QFont("Arial")

    def init_ui(self):
        title_label = QLabel("How To Meow", self)
        title_font = QFont(self.barriecito_font)
        title_font.setBold(True)
        title_font.setPointSize(90)
        title_label.setFont(title_font)
        title_label.setStyleSheet(
            f"color: rgb({self.accent_color.red()}, {self.accent_color.green()}, {self.accent_color.blue()});"
        )
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setGeometry(0, 80, 1600, 120)

        desc_panel = RoundedPanel(radius=30, bg_color=self.accent_color, parent=self)
        desc_panel.setGeometry(400, 250, 800, 450)

        desc_text = QTextEdit(desc_panel)
        desc_text.setReadOnly(True)
        desc_text.setStyleSheet("background: transparent; border: none; color: white;")
        desc_text.setFont(QFont(self.barriecito_font.family(), 24))
        desc_text.setGeometry(0, 0, 800, 450)
        desc_text.setText(
            "Ready to sharpen your claws and outsmart the other cats? When at least two cats join within 10 seconds, the guessing game begins!\n\n"
            "A secret word appears and it's your job to sniff it out—one letter at a time.\n\n"
            "Each wrong guess? That's one of your nine lives gone—well, you only get 5!\n"
            "And don't nap too long—you've got 30 seconds to crack the code.\n\n"
            "Guess the word first and you win the round. First kitty to win 3 rounds gets the crown!"
        )
        desc_text.setContentsMargins(40, 30, 40, 30)

        meow_button = RoundedButton("Meow", self)
        meow_button.setFont(QFont(self.barriecito_font.family(), 32))
        meow_button.setStyleSheet("color: white;")
        meow_button.move(650, 740)
        meow_button.clicked.connect(self.on_meow_clicked)

        # Paths relative to res/
        left_cat = self.load_scaled_image("images/cat3.png", 300, 300)
        right_cat = self.load_scaled_image("images/cat3.png", 300, 300)

        if left_cat:
            left_cat_label = QLabel(self)
            left_cat_label.setPixmap(left_cat)
            left_cat_label.setGeometry(100, 350, 300, 300)

        if right_cat:
            right_cat_label = QLabel(self)
            right_cat_label.setPixmap(right_cat)
            right_cat_label.setGeometry(1200, 350, 300, 300)

        self.add_paw_prints()

    def load_scaled_image(self, relative_path, width, height):
        # Go two levels up from current file directory, then into res/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "res"))
        abs_path = os.path.join(base_path, relative_path)
        if os.path.exists(abs_path):
            pixmap = QPixmap(abs_path)
            return pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            print(f"Error loading image: {relative_path}")
            return None

    def add_paw_prints(self):
        paw_positions = [
            (120, 180), (220, 150), (1300, 200), (1400, 160),
            (200, 850), (300, 880), (1300, 850), (1400, 880)
        ]
        paw_pixmap = self.load_scaled_image("images/paw__print.png", 60, 60)
        if not paw_pixmap:
            return
        for x, y in paw_positions:
            label = QLabel(self)
            label.setPixmap(paw_pixmap)
            label.setGeometry(x, y, 60, 60)

    def on_meow_clicked(self):
        print(f"Meow clicked! Username: {self.username}")
        self.close()

class HowToPanel:
    pass