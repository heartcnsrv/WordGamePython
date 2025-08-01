import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QApplication
)
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase

class LobbyView(QWidget):
    ICON_WIDTH = 300
    ICON_HEIGHT = 300

    def __init__(self):
        super().__init__()
        self.dot_count = 0
        self.original_message = ""
        self.restart_button = None
        self.main_menu_button = None
        self.button_layout = None

        self.setWindowTitle("Lobby")
        self.resize(1100, 700)
        self.center()

        self.load_custom_font()
        self.setStyleSheet("background-color: white;")
        self.setup_ui()

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_dots)
        self.animation_timer.start(500)

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.primaryScreen()
        centerPoint = screen.availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def load_custom_font(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "../../"))
        font_path = os.path.join(project_root, "res", "Barriecito-Regular.ttf")
        self.custom_font_family = "Sans Serif"
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                self.custom_font_family = families[0]
        else:
            print("Font not found:", font_path)

    def setup_ui(self):
        self.setMinimumSize(1100, 700)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "../../"))
        image_path = os.path.join(project_root, "res", "images", "catmoon2.png")
        cat_pixmap = self.load_and_scale_icon(image_path)

        # Positions of icons
        self.top_left_label = QLabel(self)
        self.top_left_label.setPixmap(cat_pixmap)
        self.top_left_label.setGeometry(20, 20, self.ICON_WIDTH, self.ICON_HEIGHT)

        self.top_right_label = QLabel(self)
        self.top_right_label.setPixmap(cat_pixmap)
        self.top_right_label.setGeometry(self.width() - self.ICON_WIDTH - 20, 20, self.ICON_WIDTH, self.ICON_HEIGHT)

        self.bottom_left_label = QLabel(self)
        self.bottom_left_label.setPixmap(cat_pixmap)
        self.bottom_left_label.setGeometry(20, self.height() - self.ICON_HEIGHT - 20, self.ICON_WIDTH, self.ICON_HEIGHT)

        self.bottom_right_label = QLabel(self)
        self.bottom_right_label.setPixmap(cat_pixmap)
        self.bottom_right_label.setGeometry(
            self.width() - self.ICON_WIDTH - 20,
            self.height() - self.ICON_HEIGHT - 20,
            self.ICON_WIDTH,
            self.ICON_HEIGHT
        )

        # Center panel setup
        self.center_panel = QWidget(self)
        self.center_panel.setStyleSheet("background-color: rgba(255, 255, 255, 240); border: 1px solid gray;")
        self.center_panel.setGeometry((self.width() - 600) // 2, (self.height() - 300) // 2, 600, 300)

        self.center_layout = QVBoxLayout()
        self.center_layout.setContentsMargins(20, 20, 20, 20)
        self.center_layout.setSpacing(20)
        self.center_panel.setLayout(self.center_layout)

        # Waiting message label
        self.message_label = QLabel("Waiting for players")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setFont(QFont(self.custom_font_family, 24))
        self.center_layout.addWidget(self.message_label)

        # Matchmaking timer label
        self.matchmaking_timer_label = QLabel()
        self.matchmaking_timer_label.setAlignment(Qt.AlignCenter)
        self.matchmaking_timer_label.setFont(QFont(self.custom_font_family, 38))
        self.matchmaking_timer_label.setVisible(False)
        self.center_layout.addWidget(self.matchmaking_timer_label)

        # Status label
        self.status_label = QLabel("Game Status: Waiting")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont(self.custom_font_family, 18))
        self.center_layout.addWidget(self.status_label)

        # Players label
        self.players_label = QLabel("Players: Waiting for opponent...")
        self.players_label.setAlignment(Qt.AlignCenter)
        self.players_label.setFont(QFont(self.custom_font_family, 18))
        self.center_layout.addWidget(self.players_label)

        # Countdown label (for start countdown)
        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(QFont(self.custom_font_family, 36))
        self.countdown_label.setVisible(False)
        self.center_layout.addWidget(self.countdown_label)

        self.center_layout.addStretch()

    def resizeEvent(self, event):
        # Reposition icons and resize center panel
        w = self.width()
        h = self.height()
        self.top_left_label.move(20, 20)
        self.top_right_label.move(w - self.ICON_WIDTH - 20, 20)
        self.bottom_left_label.move(20, h - self.ICON_HEIGHT - 20)
        self.bottom_right_label.move(w - self.ICON_WIDTH - 20, h - self.ICON_HEIGHT - 20)
        self.center_panel.setGeometry((w - 600) // 2, (h - 300) // 2, 600, 300)
        super().resizeEvent(event)

    def load_and_scale_icon(self, file_path):
        if os.path.exists(file_path):
            pixmap = QPixmap(file_path)
        else:
            print("Image not found:", file_path)
            pixmap = QPixmap(self.ICON_WIDTH, self.ICON_HEIGHT)
            pixmap.fill(Qt.transparent)
        return pixmap.scaled(self.ICON_WIDTH, self.ICON_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def animate_dots(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = '.' * self.dot_count
        if self.message_label.text().startswith("Waiting"):
            self.message_label.setText(f"Waiting for players{dots}")

    def update_waiting_message(self, message):
        if message is None:
            message = "Waiting for players..."
        self.message_label.setText(message)

        # Set color based on message content
        if "ERROR" in message or "failed" in message:
            self.message_label.setStyleSheet("color: rgb(200, 0, 0);")
        elif "Connected" in message or "Starting" in message:
            self.message_label.setStyleSheet("color: rgb(0, 150, 0);")
        elif "Waiting" in message:
            self.message_label.setStyleSheet("color: rgb(0, 0, 150);")
        else:
            self.message_label.setStyleSheet("color: black;")

        # Animate dots if waiting
        if "Waiting" in message:
            if not self.animation_timer.isActive():
                self.animation_timer.start()
        else:
            self.animation_timer.stop()

    def update_status(self, status):
        if status is None:
            self.status_label.setText("Game Status: Unknown")
            return
        mapping = {
            "WAITING": ("Waiting for Players", "color: rgb(0, 0, 150);"),
            "PLAYING": ("Game Starting", "color: rgb(0, 150, 0);"),
            "CONNECTING": ("Connecting...", "color: rgb(150, 100, 0);"),
            "RETRY": ("Connection Failed - Retrying", "color: rgb(150, 0, 0);"),
            "ERROR": ("Connection Error", "color: rgb(200, 0, 0);"),
        }
        display_status, style = mapping.get(status, (status, "color: black;"))
        self.status_label.setText("Game Status: " + display_status)
        self.status_label.setStyleSheet(style)

    def update_players_list(self, players):
        if not players:
            self.players_label.setText("Players: Waiting for players...")
            self.players_label.setStyleSheet("color: gray;")
        elif len(players) == 1:
            self.players_label.setText(f"Players: {players[0]} (Waiting for opponent)")
            self.players_label.setStyleSheet("color: black;")
        else:
            self.players_label.setText(f"Players: {', '.join(players)}")
            self.players_label.setStyleSheet("color: black;")

    def show_restart_and_main_menu_buttons(self):
        self.animate_dots()
        if self.button_layout is None:
            self.button_layout = QHBoxLayout()
            self.button_layout.setContentsMargins(0, 20, 0, 0)
            self.button_layout.setSpacing(20)
            self.button_layout.addStretch()

            self.restart_button = QPushButton("Find Match Again")
            self.restart_button.setFont(QFont(self.custom_font_family, 16))
            self.restart_button.setFixedSize(200, 40)
            self.restart_button.setStyleSheet("""
                QPushButton {
                    background-color: #009600;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #007700;
                }
            """)
            self.button_layout.addWidget(self.restart_button)

            self.main_menu_button = QPushButton("Return to Main Menu")
            self.main_menu_button.setFont(QFont(self.custom_font_family, 16))
            self.main_menu_button.setFixedSize(200, 40)
            self.main_menu_button.setStyleSheet("""
                QPushButton {
                    background-color: #e6e6e6;
                    color: black;
                    border: 1px solid #c8c8c8;
                    border-radius: 5px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #d8d8d8;
                }
            """)
            self.button_layout.addWidget(self.main_menu_button)

            self.button_layout.addStretch()
            self.center_layout = self.layout()  # assuming center_layout is the main vertical layout
            self.center_layout.addLayout(self.button_layout)
        else:
            self.restart_button.show()
            self.main_menu_button.show()

        self.update_waiting_message("No meow found")

    def hide_restart_and_main_menu_buttons(self):
        if self.restart_button:
            self.restart_button.hide()
        if self.main_menu_button:
            self.main_menu_button.hide()

    def remove_restart_and_main_menu_buttons(self):
        if self.button_layout:
            while self.button_layout.count():
                item = self.button_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.layout().removeItem(self.button_layout)
            self.button_layout.deleteLater()
            self.button_layout = None

        self.restart_button = None
        self.main_menu_button = None