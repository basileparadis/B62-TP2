import sqlite3


class DAO_SQLite:

    def __init__(self):
        self.connection = sqlite3.connect('synonymes.db')
        self.cursor = self.connection.cursor()
        self.CHEMINBD = './synonymes.db'
        # DÉCLARATIONS SQL
        self.DROP_MOTS = "DROP TABLE mots"
        self.DROP_MATRICE = "DROP TABLE matrice"
        self.ENABLE_FK = 'PRAGMA foreign_keys = 1'
        self.SELECT_ALL_MATRICE = "SELECT * FROM matrice"
        self.SELECT_ALL_MATRICE_2 = "SELECT index_ligne, index_colonne, score FROM matrice WHERE taille_fenetre = :1"
        self.INSERT_MATRICE = "INSERT INTO matrice VALUES (:1, :2, :3, :4)"
        self.MAJ_MATRICE = "UPDATE matrice SET score = :1 WHERE index_ligne = :2 " \
                           "AND index_colonne = :3 " \
                           "AND taille_fenetre = :4 "
        self.INDEX_LIGNE = 0
        self.INDEX_COLONNE = 1
        self.SCORE = 3

    def connecter(self, CHEMINBD):
        connexion = sqlite3.connect(CHEMINBD)
        curseur = connexion.cursor()
        curseur.execute(self.ENABLE_FK)
        return connexion, curseur

    def creer_table(self):
        try:
            self.cursor.execute(self.DROP_MOTS)
            self.cursor.execute(self.DROP_MATRICE)
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
            self.creer_table()
            resultat = self.cursor.execute("SELECT index_mot, mot FROM mots")

        for index, mot in resultat:
            dictionnaire[mot] = index
        for mot in liste_texte:
            if mot not in dictionnaire:
                nouvelle_liste.append((len(dictionnaire), mot))
                dictionnaire[mot] = len(dictionnaire)

        self.cursor.executemany("INSERT INTO mots VALUES (:1, :2)", nouvelle_liste)
        self.connection.commit()
        return dictionnaire

    def inserer_matrice(self, dico):
        liste_insertions = []
        liste_MaJ = []
        dictionnaire = self.construire_dictionnaire_de_matrice()
        for key, score in dico.items():
            if key in dictionnaire:
                newScore = score + dictionnaire[key]
                liste_MaJ.append((newScore, key[0], key[1], key[2]))
            else:
                liste_insertions.append((key[0], key[1], key[2], score))
        self.cursor.executemany(self.INSERT_MATRICE, liste_insertions)
        if liste_MaJ:
            self.cursor.executemany(self.MAJ_MATRICE, liste_MaJ)
        self.connection.commit()

    def construire_dictionnaire_de_matrice(self):
        dico_de_bd = {}
        try:
            cur = self.cursor
            cur.execute(self.SELECT_ALL_MATRICE)
            rows = cur.fetchall()
            for row in rows:
                dico_de_bd[(row[0], row[1], row[2])] = row[3]
        finally:
            return dico_de_bd

    def importer_matrice_bd(self, taille_fenetre):
        data = []
        try:
            cur = self.cursor
            cur.execute(self.SELECT_ALL_MATRICE_2, (int(taille_fenetre),))
            rows = cur.fetchall()
            for row in rows:
                ligne = row[self.INDEX_LIGNE]
                colonne = row[self.INDEX_COLONNE]
                score = row[self.SCORE]
                data.append((ligne, colonne, score))
        finally:
            return data
