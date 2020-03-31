import sqlite3


class DAO_SQLite():
    def __init__(self):
        self.connection = sqlite3.connect("synonymes.db")
        self.cursor = self.connection.cursor()