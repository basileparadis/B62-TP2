import argparse
import getopt
import sys
import numpy as np
import stopWords
from DAO_BD import DAO_SQLite
import lecture as Lecture


class Controlleur:
    def __init__(self, arguments):
        self.argDict = dict.fromkeys(["mode", "window", "encoding", "path"])
        self.arguments = arguments
        self.bd = DAO_SQLite()
        self.liste_mots = None
        self.matrice = None
        self.parser = None
        self.fenetre = None
        self.indexes = None

    def parse(self):
        self.parser = argparse.ArgumentParser(description='Cooccurences de mots dans un texte.',
                                              conflict_handler='resolve')
        self.parser.add_argument('-bd', action='store_true', help='réinitialise la BD à son état initial')
        self.parser.add_argument('-e', action='store_true', help='mode entraînement')
        self.parser.add_argument('-t', '--fenetre', type=int, help='taille de la fenêtre', metavar='<taille>')
        self.parser.add_argument('--enc', help='encodage du fichier', metavar='<encodage>')
        self.parser.add_argument('-c', '--chemin', help='chemin du corpus d’entraînement', metavar='<chemin>')

        args = vars(self.parser.parse_args())

        entrainement = args['e']
        chemin = args['chemin']
        encodage = args['enc']
        self.fenetre = args['fenetre']
        recreerBD = args['bd']

        self.process(entrainement, chemin, encodage, recreerBD)

    def process(self, entrainement, chemin, encodage, recreerBD):

        if recreerBD:
            self.bd.creer_table()
            print('\n*BASE DE DONNÉES RECRÉE*')
        if entrainement is False:
            print('\nAucun mode choisi')
            self.parser.print_help()
            sys.exit()
        elif entrainement is True and (chemin is None or encodage is None or self.fenetre is None):
            print('\nVous devez définir -t --enc et --chemin')
            sys.exit()
        else:
            print(str(chemin) + ' ' + str(encodage) + ' ' + str(self.fenetre))
            print('\nEntrez un mot, le nombre de synonymes que vous voulez et la méthode de calcul.'
                  '\n\nProduit scalaire = 0, Least-Squares = 1, City-Block = 2, Quitter = "q"\n')

            saisie = input().lower()
            if saisie == 'q':
                sys.exit()
            else:
                try:
                    leMot, nbSyn, methodeCalc = saisie.split()

                    self.liste_mots = Lecture.liste_mots(chemin, encodage)
                    # print(listeMots)
                    self.indexes = self.bd.inserer_dict(self.liste_mots)
                    self.bd.inserer_matrice(self.findCooccurences())

                    # matrice = remplirMatrice(mainFichierTxt, dictionnaire, {}, int(tailleFenetre))
                    # calculerScores(leMot, dictionnaire, matrice, methodeCalc)

                except getopt.GetoptError as err:
                    print(err)
                    sys.exit()
                except ValueError:
                    print('Les options entrées sont invalides')
                    sys.exit()

    def findCooccurences(self):
        dico = {}
        tailleFenetre = self.fenetre // 2
        for i in range(len(self.liste_mots)):
            index_mot = self.indexes[self.liste_mots[i]]
            for j in range(1, tailleFenetre):
                if j != index_mot:
                    try:
                        tempIndex = self.indexes[self.liste_mots[i + j]]
                        if tempIndex <= index_mot:
                            key = (tempIndex, index_mot, self.fenetre)
                            if key not in dico:
                                dico[key] = 1
                            else:
                                dico[key] = dico[key] + 1
                        tempIndex = self.indexes[self.liste_mots[i - j]]
                        if tempIndex <= index_mot:
                            key = (tempIndex, index_mot, self.fenetre)
                            if key not in dico:
                                dico[key] = 1
                            else:
                                dico[key] = dico[key] + 1
                    except IndexError:
                        pass
        return dico

    # Remplir la matrice de cooccurence en utilisant la fenêtre
    def remplirMatrice(self, texte, dictionnaire, matriceMot, tailleFenetre):
        tailleTexte = len(texte)  # Le nombre de mots dans la liste de mots du texte

        # Pour ne pas dépasser l'index
        for i in range(tailleTexte - tailleFenetre):
            # La position du mot au centre de la fenêtre
            indexMotMilieu = dictionnaire[texte[i + tailleFenetre]]

            for j in range(tailleFenetre):
                if i - j >= 0:
                    indexMotCompare = dictionnaire[texte[i - j]]
                    matriceMot[indexMotMilieu][indexMotCompare] += 1
                if i + j < tailleTexte:
                    indexMotCompare = dictionnaire[texte[i + j]]
                    matriceMot[indexMotMilieu][indexMotCompare] += 1

        return matriceMot

    # Trouve les meilleurs résultats à partir du mot et de l'algorithme passés en paramètres.
    def calculerScores(self, motRech, dictionnaire, matriceMot, algo):
        scores = []
        # Recherche de l'index du mot sélectionné
        indexMotCompare = int(dictionnaire[motRech])

        for mot, index in dictionnaire.items():
            if mot == motRech or mot in stopWords:
                continue
            else:
                result = algo(matriceMot[indexMotCompare], matriceMot[index])
                scores.append((mot, result))

        return scores

    # Algorithme produit scalaire
    def produitScalaire(self, vector1, vector2):
        return np.dot(vector1, vector2)

    # Algorithme least-squares
    def leastSquare(self, vector1, vector2):
        return np.sum((vector1 - vector2) ** 2)

    # Algorithme city-block
    def cityBlock(self, vector1, vector2):
        return np.sum(np.abs(vector1 - vector2))
