import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt


class LeaderboardsView(QWidget):
    def __init__(self):
        super().__init__()
        self.custom_font_family = "Sans Serif"
        self.load_custom_font()
        self.init_ui()

    def load_custom_font(self):
        # Use absolute path based on this file location
        base_path = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.normpath(os.path.join(base_path, "..", "..", "res", "Barriecito-Regular.ttf"))

        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                self.custom_font_family = families[0]
        else:
            print(f"Could not find Barriecito-Regular.ttf font file at {font_path}")

    def init_ui(self):
        self.setWindowTitle("Meowstery Leaderboard")
        self.resize(700, 500)
        self.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("MEOWBOARD")
        title_font = QFont(self.custom_font_family, 40)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Username", "Meows"])
        self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setShowGrid(True)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("background-color: white; color: black;")

        header_font = QFont(self.custom_font_family, 24)
        self.table_widget.horizontalHeader().setFont(header_font)
        self.table_widget.horizontalHeader().setStyleSheet(
            "QHeaderView::section { background-color: black; color: white; }"
        )
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setFont(QFont(self.custom_font_family, 18))
        self.table_widget.setFixedHeight(400)
        self.table_widget.setSortingEnabled(False)
        self.table_widget.verticalHeader().setDefaultSectionSize(30)

        for col in range(self.table_widget.columnCount()):
            self.table_widget.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

        main_layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        back_button = QPushButton("Back")
        back_button.setFont(QFont(self.custom_font_family, 16))
        back_button.setFixedSize(100, 40)
        back_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #000000;
                border-radius: 10px;
                background-color: white;
                color: black;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        back_button.clicked.connect(self.close)

        button_layout.addWidget(back_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def add_leaderboard_entry(self, username, meows):
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)

        username_item = QTableWidgetItem(username)
        meows_item = QTableWidgetItem(str(meows))

        username_item.setTextAlignment(Qt.AlignCenter)
        meows_item.setTextAlignment(Qt.AlignCenter)

        self.table_widget.setItem(row, 0, username_item)
        self.table_widget.setItem(row, 1, meows_item)