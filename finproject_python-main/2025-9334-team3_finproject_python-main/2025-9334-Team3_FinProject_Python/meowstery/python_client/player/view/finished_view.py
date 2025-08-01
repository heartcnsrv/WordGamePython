from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFrame, QApplication
)
from PyQt5.QtGui import QFont, QPixmap, QColor, QFontDatabase
from PyQt5.QtCore import Qt
import os
import sys


class GameFinishedView(QWidget):
    def __init__(self, player_names):
        super().__init__()
        self.player_names = player_names
        self.player_scores = [0] * len(player_names)
        self.word_labels = []
        self.current_word = ""
        self.custom_font = None

        self._load_custom_font()
        self._init_ui()

    def _load_custom_font(self):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_path = os.path.join(base_path, "res", "Barriecito-Regular.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    self.custom_font = families[0]
        if not self.custom_font:
            print("Using fallback font")
            self.custom_font = "Arial"

    def _init_ui(self):
        self.setWindowTitle("Meowstery Game - Results")
        self.resize(1200, 700)
        self.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 20, 40, 20)
        self.setLayout(main_layout)

        title_label = QLabel("Game Results")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(self.custom_font, 64, QFont.Bold))
        main_layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Left panel - Player scores
        self.scores_panel = QFrame()
        self.scores_panel.setStyleSheet("background-color: white;")
        self.scores_panel.setFixedWidth(200)
        scores_layout = QVBoxLayout()
        scores_layout.setContentsMargins(0, 20, 0, 0)
        self.scores_panel.setLayout(scores_layout)

        scores_title = QLabel("Final Scores")
        scores_title.setFont(QFont(self.custom_font, 28, QFont.Bold))
        scores_title.setAlignment(Qt.AlignCenter)
        scores_layout.addWidget(scores_title)
        scores_layout.addSpacing(20)

        content_layout.addWidget(self.scores_panel)

        # Center panel - Result message and word display
        center_panel = QVBoxLayout()
        content_layout.addLayout(center_panel, 1)

        self.result_message = QLabel()
        self.result_message.setAlignment(Qt.AlignCenter)
        self.result_message.setFont(QFont(self.custom_font, 48, QFont.Bold))
        center_panel.addWidget(self.result_message)

        self.word_display_panel = QHBoxLayout()
        self.word_display_panel.setAlignment(Qt.AlignCenter)
        center_panel.addLayout(self.word_display_panel)

        # Bottom panel - Close button and cat image
        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch(1)

        self.close_button = QPushButton("Return to Main Menu")
        self.close_button.setFont(QFont(self.custom_font, 24, QFont.Bold))
        self.close_button.setFixedSize(300, 60)
        bottom_panel.addWidget(self.close_button)
        bottom_panel.addSpacing(20)

        # Cat image with correct fixed path
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cat_path = os.path.join(base_path, "res", "images", "16.png")
        if os.path.exists(cat_path):
            cat_pixmap = QPixmap(cat_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cat_label = QLabel()
            cat_label.setPixmap(cat_pixmap)
            bottom_panel.addWidget(cat_label)
        else:
            print(f"Image not found at: {cat_path}")

        bottom_panel.addStretch(1)
        main_layout.addLayout(bottom_panel)

        self._update_player_scores()

    def set_word_display(self, word):
        self.current_word = word or ""

        # Clear previous word
        while self.word_display_panel.count():
            item = self.word_display_panel.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        intro_label = QLabel("The word was:")
        intro_label.setFont(QFont(self.custom_font, 24))
        self.word_display_panel.addWidget(intro_label)

        for letter in self.current_word.upper():
            letter_label = QLabel(letter)
            letter_label.setFont(QFont(self.custom_font, 60, QFont.Bold))
            letter_label.setFixedSize(60, 80)
            letter_label.setAlignment(Qt.AlignCenter)
            self.word_display_panel.addWidget(letter_label)

    def _update_player_scores(self):
        # Clear existing score labels except title and spacing
        while self.scores_panel.layout().count() > 2:
            item = self.scores_panel.layout().takeAt(2)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for name, score in zip(self.player_names, self.player_scores):
            score_label = QLabel(f"{name}: {score}")
            score_label.setFont(QFont(self.custom_font, 24, QFont.Bold))
            score_label.setStyleSheet("padding: 5px 0 5px 10px;")
            self.scores_panel.layout().addWidget(score_label)

    def update_player_scores_with_highlight(self):
        # Clear existing score labels except title and spacing
        while self.scores_panel.layout().count() > 2:
            item = self.scores_panel.layout().takeAt(2)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        winner_index = self._get_winner_index()

        for i, (name, score) in enumerate(zip(self.player_names, self.player_scores)):
            score_label = QLabel(f"{name}: {score}")
            score_label.setFont(QFont(self.custom_font, 24, QFont.Bold))
            style = "padding: 5px 0 5px 10px;"
            if i == winner_index:
                style = "color: rgb(0, 150, 0); padding: 5px 0 5px 10px;"
                score_label.setText(f"{score_label.text()} 👑")
            score_label.setStyleSheet(style)
            self.scores_panel.layout().addWidget(score_label)

    def _get_winner_index(self):
        if not self.player_scores:
            return -1
        max_score = max(self.player_scores)
        return self.player_scores.index(max_score)

    def set_player_score(self, player_name, score):
        for i, name in enumerate(self.player_names):
            if name == player_name:
                self.player_scores[i] = score
                break
        self.update_player_scores_with_highlight()

    def set_result_message(self, message, is_winner):
        self.result_message.setText(message)
        color = "rgb(0, 150, 0)" if is_winner else "rgb(200, 0, 0)"
        self.result_message.setStyleSheet(f"color: {color};")

    def show_popup_message(self, message, is_winner):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Result")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)

        color = QColor(0, 150, 0) if is_winner else QColor(200, 0, 0)
        msg_box.setStyleSheet(
            f"QLabel {{ color: {color.name()}; font-weight: bold; font-size: 24pt; }}"
            "QPushButton { font-size: 14pt; min-width: 100px; }"
        )
        msg_box.exec_()

    def set_close_button_listener(self, callback):
        self.close_button.clicked.connect(callback)

    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()

    def dispose(self):
        self.close()


def main():
    app = QApplication(sys.argv)
    players = ["Player 1", "Player 2", "Player 3"]
    view = GameFinishedView(players)
    view.set_player_score("Player 1", 15)
    view.set_player_score("Player 2", 20)  # Winner
    view.set_player_score("Player 3", 10)
    view.set_result_message("Player 2 wins!", True)
    view.set_word_display("PYTHON")
    view.set_close_button_listener(app.quit)
    view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
