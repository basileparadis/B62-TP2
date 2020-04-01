import sqlite3


class DAO_SQLite():
    def __init__(self):
        self.connection = sqlite3.connect("synonymes.db")
        self.cursor = self.connection.cursor()

    def inserer_dict(self):
        pass

    def inserer_matrice(self):
        pass

    def sauvegarder_matrice(self):
        pass

    def recreer_table(self):
        pass
