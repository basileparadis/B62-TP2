import sqlite3


class DAO_SQLite():
    def __init__(self):
        self.connection = sqlite3.connect("synonymes.db")
        self.cursor = self.connection.cursor()

    def recreer_table(self):
        try:
            self.cursor.execute("DROP TABLE mots")
            self.cursor.execute("DROP TABLE matrice")
        except:
            pass
        finally:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS mots (index_mot INT PRIMARY KEY, mot TEXT)")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS matrice ( index_ligne INT, index_colonne INT, 
            taille_fenetre INT, score INT, CONSTRAINT pk_matrice PRIMARY KEY (index_ligne, index_colonne, 
            taille_fenetre), FOREIGN KEY(index_ligne) REFERENCES mots(index_mot), FOREIGN KEY(index_colonne) 
            REFERENCES mots(index_mot))""")

    def inserer_dict(self, liste_texte):
        dictionnaire = {}
        nouvelle_liste = []
        try:
            resultat = self.cursor.execute("SELECT index_mot, mot FROM mots")
        except:
            self.recreer_table()
            resultat = self.cursor.execute("SELECT index_mot, mot FROM mots")

        for index, mot in resultat:
            dictionnaire[mot] = index
        for mot in liste_texte:
            if mot not in dictionnaire:
                nouvelle_liste.append(len(dictionnaire), mot)
                dictionnaire[mot] = len(dictionnaire)

        self.cursor.executemany("INSERT INTO mots VALUES (:1, :2)", nouvelle_liste)
        self.connection.commit()
        return dictionnaire

    def inserer_matrice(self):
        liste_insertions = []
        liste_MaJ = []
        pass

    def sauvegarder_matrice(self):
        pass
