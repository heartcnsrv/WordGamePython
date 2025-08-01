import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QMainWindow
)


class KeyboardPanel(QWidget):
    def __init__(self, font):
        super().__init__()
        self.buttons = {}
        self.font = font
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        layout.setSpacing(10)

        # First row (10 letters)
        for i, letter in enumerate("ABCDEFGHIJ"):
            btn = self.create_letter_button(letter)
            self.buttons[letter] = btn
            layout.addWidget(btn, 0, i)

        # Second row (9 letters, offset by 1)
        for i, letter in enumerate("KLMNOPQRS"):
            btn = self.create_letter_button(letter)
            self.buttons[letter] = btn
            layout.addWidget(btn, 1, i + 1)

        # Third row (7 letters, offset by 2)
        for i, letter in enumerate("TUVWXYZ"):
            btn = self.create_letter_button(letter)
            self.buttons[letter] = btn
            layout.addWidget(btn, 2, i + 2)

        self.setLayout(layout)

    def create_letter_button(self, letter):
        btn = QPushButton(letter)
        btn.setFont(self.font)
        btn.setFixedSize(60, 60)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 5px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #dddddd;
                color: #888888;
            }
        """)
        return btn

    def disable_letter_button(self, letter, is_correct):
        letter = letter.upper()
        if letter in self.buttons:
            btn = self.buttons[letter]
            btn.setDisabled(True)
            if is_correct:
                btn.setStyleSheet("""
                    QPushButton:disabled {
                        background-color: #a5d6a7;
                        color: #2e7d32;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton:disabled {
                        background-color: #ef9a9a;
                        color: #c62828;
                    }
                """)

    def reset(self):
        for letter, btn in self.buttons.items():
            btn.setDisabled(False)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:disabled {
                    background-color: #dddddd;
                    color: #888888;
                }
            """)

    def disable_all_buttons(self):
        for btn in self.buttons.values():
            btn.setDisabled(True)

    def set_letter_button_listener(self, callback):
        for letter, btn in self.buttons.items():
            # Capture letter correctly in lambda
            btn.clicked.connect(lambda _, l=letter: callback(l))


class WordDisplayPanel(QWidget):
    def __init__(self, font):
        super().__init__()
        self.font = font
        self.labels = []
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()
        self.layout.setSpacing(15)
        self.setLayout(self.layout)

    def set_word_length(self, length):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.labels = []

        for _ in range(length):
            label = QLabel("_")
            label.setFont(self.font)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    border-bottom: 3px solid #333333;
                    padding: 0 10px;
                    min-width: 40px;
                    font-size: 36px;
                }
            """)
            self.labels.append(label)
            self.layout.addWidget(label)

    def reveal_letter(self, letter, position):
        if 0 <= position < len(self.labels):
            self.labels[position].setText(letter.upper())

    def update_word_display(self, masked_word):
        for i, char in enumerate(masked_word):
            if i < len(self.labels):
                self.labels[i].setText(char.upper() if char != '_' else "_")


class PlayerScoresPanel(QWidget):
    def __init__(self, players, font):
        super().__init__()
        self.font = font
        self.labels = {}
        self.initUI(players)

    def initUI(self, players):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Player Scores")
        title.setFont(self.font)
        title.setStyleSheet("font-weight: bold; font-size: 24px;")
        layout.addWidget(title)

        for player in players:
            lbl = QLabel(f"{player}: 0")
            lbl.setFont(self.font)
            lbl.setStyleSheet("font-size: 20px;")
            self.labels[player] = lbl
            layout.addWidget(lbl)

        layout.addStretch()
        self.setLayout(layout)

    def update_score(self, player, score):
        if player in self.labels:
            self.labels[player].setText(f"{player}: {score}")


class LivesIndicatorPanel(QWidget):
    def __init__(self, font):
        super().__init__()
        self.font = font
        self.lives = 5
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.label = QLabel(f"Lives: {self.lives}")
        self.label.setFont(self.font)
        self.label.setStyleSheet("font-size: 24px;")

        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_lives(self, lives):
        self.lives = lives
        self.label.setText(f"Lives: {lives}")

    def reset(self):
        self.update_lives(5)


class RoundInfoPanel(QWidget):
    def __init__(self, font):
        super().__init__()
        self.font = font
        self.round_num = 1
        self.time_remaining = 30
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)

        self.round_label = QLabel(f"Round: {self.round_num}")
        self.round_label.setFont(self.font)
        self.round_label.setStyleSheet("font-size: 24px;")

        self.timer_label = QLabel(f"Time: {self.time_remaining}")
        self.timer_label.setFont(self.font)
        self.timer_label.setStyleSheet("font-size: 24px;")

        layout.addWidget(self.round_label)
        layout.addWidget(self.timer_label)
        self.setLayout(layout)

    def update_round(self, round_num):
        self.round_num = round_num
        self.round_label.setText(f"Round: {round_num}")

    def update_timer(self, time):
        self.time_remaining = time
        self.timer_label.setText(f"Time: {time}")

    def reset_timer(self, time):
        self.update_timer(time)


class GameOverlayPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: rgba(255, 255, 255, 240);")
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.main_layout)

    def set_content(self, widget):
        for i in reversed(range(self.main_layout.count())):
            w = self.main_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.main_layout.addWidget(widget)


class GameView(QMainWindow):
    def __init__(self, players):
        super().__init__()
        self.setWindowTitle("Meowstery Game")
        self.setFixedSize(1500, 900)

        self.custom_font = self.load_custom_font()
        self.current_round = 1
        self.time_remaining = 30
        self.word_length = 0
        self.lives_remaining = 5

        self.guessed_letters_label = None  # Add attribute for guessed letters display

        self.initUI(players)

    def load_custom_font(self):
        font_paths = [
            "meowstery/python_client/res/Barriecito-Regular.ttf",
            "meowstery/res/Barriecito-Regular.ttf",
            "res/Barriecito-Regular.ttf"
        ]
        font_id = -1
        for path in font_paths:
            if os.path.exists(path):
                font_id = QFontDatabase.addApplicationFont(path)
                if font_id != -1:
                    break
        if font_id == -1:
            return QFont("Arial", 20)
        family = QFontDatabase.applicationFontFamilies(font_id)[0]
        return QFont(family, 20)

    def initUI(self, players):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Add guessed letters label above word display
        self.guessed_letters_label = QLabel("")
        self.guessed_letters_label.setFont(QFont(self.custom_font.family(), 28, QFont.Bold))
        self.guessed_letters_label.setAlignment(Qt.AlignCenter)
        self.guessed_letters_label.setStyleSheet("color: #2e7d32; letter-spacing: 8px; margin-bottom: 10px;")
        main_layout.addWidget(self.guessed_letters_label, alignment=Qt.AlignCenter)

        # Round info
        self.round_info_panel = RoundInfoPanel(self.custom_font)
        main_layout.addWidget(self.round_info_panel, alignment=Qt.AlignCenter)

        # Word display
        self.word_display_panel = WordDisplayPanel(self.custom_font)
        main_layout.addWidget(self.word_display_panel, alignment=Qt.AlignCenter)

        # Keyboard panel
        self.keyboard_panel = KeyboardPanel(self.custom_font)
        main_layout.addWidget(self.keyboard_panel, alignment=Qt.AlignCenter)

        # Lives indicator
        self.lives_indicator_panel = LivesIndicatorPanel(self.custom_font)
        main_layout.addWidget(self.lives_indicator_panel, alignment=Qt.AlignCenter)

        # Optional: Add paw print image below lives indicator
        paw_label = QLabel()
        paw_path = "meowstery/python_client/res/images/paw__print.png"
        if os.path.exists(paw_path):
            pixmap = QPixmap(paw_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            paw_label.setPixmap(pixmap)
            paw_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(paw_label, alignment=Qt.AlignCenter)

        main_widget.setLayout(main_layout)

        # Player scores on right side
        self.player_scores_panel = PlayerScoresPanel(players, self.custom_font)
        self.player_scores_panel.setFixedWidth(250)

        container = QWidget()
        container_layout = QHBoxLayout()
        container_layout.addWidget(main_widget)
        container_layout.addWidget(self.player_scores_panel)
        container.setLayout(container_layout)

        self.setCentralWidget(container)

        # Overlay for messages
        self.overlay_panel = GameOverlayPanel()
        self.overlay_panel.setParent(self)
        self.overlay_panel.setGeometry(0, 0, 1500, 900)
        self.overlay_panel.hide()

    def set_word_length(self, length):
        self.word_length = length
        self.word_display_panel.set_word_length(length)

    def reveal_letter(self, letter, position):
        self.word_display_panel.reveal_letter(letter, position)

    def update_word_display(self, masked_word):
        self.word_display_panel.update_word_display(masked_word)

    def disable_letter_button(self, letter, is_correct):
        self.keyboard_panel.disable_letter_button(letter, is_correct)

    def disable_all_letter_buttons(self):
        self.keyboard_panel.disable_all_buttons()

    def reset(self):
        """Reset all buttons to initial state"""
        for letter, btn in self.buttons.items():
            btn.setEnabled(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:disabled {
                    background-color: #dddddd;
                    color: #888888;
                }
            """)

    def reset_keyboard(self):
        self.keyboard_panel.reset()

    def update_score(self, player, score):
        self.player_scores_panel.update_score(player, score)

    def update_lives(self, lives):
        self.lives_remaining = lives
        self.lives_indicator_panel.update_lives(lives)

    def update_round(self, round_num):
        self.current_round = round_num
        self.round_info_panel.update_round(round_num)

    def update_timer(self, time):
        self.time_remaining = time
        self.round_info_panel.update_timer(time)

    def show_overlay_message(self, message):
        label = QLabel(message)
        label.setFont(QFont(self.custom_font.family(), 28, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        self.overlay_panel.set_content(label)
        self.overlay_panel.show()

    def hide_overlay(self):
        self.overlay_panel.hide()

    def set_letter_button_listener(self, callback):
        self.keyboard_panel.set_letter_button_listener(callback)

    def update_guessed_letters_display(self, guessed_letters):
        """Update the guessed letters label above the word display."""
        if self.guessed_letters_label is not None:
            if guessed_letters:
                # Show guessed letters, separated by spaces
                self.guessed_letters_label.setText("Guessed: " + " ".join(sorted(guessed_letters)))
            else:
                self.guessed_letters_label.setText("")


def main():
    app = QApplication(sys.argv)

    players = ["Player 1", "Player 2", "Player 3"]
    game_view = GameView(players)

    def on_letter_clicked(letter):
        # Handle letter clicked
        # For testing, disable the button without message box
        print(f"Letter clicked: {letter}")
        game_view.disable_letter_button(letter, is_correct=True)

    game_view.set_word_length(7)
    game_view.set_letter_button_listener(on_letter_clicked)
    game_view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
