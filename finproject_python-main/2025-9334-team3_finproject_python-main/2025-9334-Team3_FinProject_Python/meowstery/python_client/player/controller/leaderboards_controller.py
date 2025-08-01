from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from typing import List
import sys

# Import the external user model which handles CORBA and data fetching
from meowstery.python_client.player.model.user_model import CorbaUserModel

# GUI View
from meowstery.python_client.player.view.leaderboards_view import LeaderboardsView


class PlayerAccount:
    """Local data structure for leaderboard entries."""
    def __init__(self, username: str, wins: int):
        self.username = username
        self.wins = wins


class LeaderboardsController:
    """Controller that connects the leaderboard view and external user model."""
    def __init__(self, view=None):
        self.model = CorbaUserModel()
        self.view = view if view else LeaderboardsView()

    def load_leaderboard_data(self):
        # Assuming CorbaUserModel has a method get_top_players() that returns
        # a List of PlayerAccount or similar objects
        players = self.model.get_top_players()
        self.populate_table(players)

    def populate_table(self, players: List[PlayerAccount]):
        table = self.view.table_widget
        table.setRowCount(0)

        for player in players:
            row = table.rowCount()
            table.insertRow(row)

            username_item = QTableWidgetItem(player.username)
            wins_item = QTableWidgetItem(str(player.wins))

            username_item.setTextAlignment(Qt.AlignCenter)
            wins_item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row, 0, username_item)
            table.setItem(row, 1, wins_item)

    def show_leaderboards_view(self):
        self.load_leaderboard_data()
        self.view.show()