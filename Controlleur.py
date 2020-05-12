import argparse
import getopt
import sys
import time

import numpy as np
from DAO_BD import DAO_SQLite
import lecture as Lecture


class Controlleur:
    def __init__(self, arguments):
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
            print('\n*BASE DE DONNÉES RECRÉÉE*')
        if entrainement is False:
            print('\nAucun mode choisi\n')
            self.parser.print_help()
            sys.exit()
        elif entrainement is True and (chemin is None or encodage is None or self.fenetre is None):
            print('\nVous devez définir -t --enc et --chemin')
            sys.exit()
        else:
            print('\n Texte: \t' + str(chemin)
                  + '\n Encodage: \t' + str(encodage)
                  + '\n Fenêtre: \t' + str(self.fenetre))
            print('\nEntrez de manière espacée un mot, le nombre de synonymes que vous voulez et la méthode de calcul.'
                  '\n\nProduit scalaire = 0, Least-Squares = 1, City-Block = 2, Quitter = "q"\n')

            saisie = input().lower()
            if saisie == 'q':
                sys.exit()
            else:
                try:
                    leMot, nbSyn, methodeCalc = saisie.split()
                    if int(methodeCalc) not in range(0, 3) or int(nbSyn) > 100:
                        print('Mauvaise saisie de donnée')
                        sys.exit()
                    else:
                        print("\nAnalyse en cours...\n")
                        debut = time.time()
                        self.liste_mots = Lecture.liste_mots(chemin, encodage)
                        self.indexes = self.bd.inserer_dict(self.liste_mots)
                        self.construire_matrice()
                        self.bd.inserer_matrice(self.trouver_cooccurrences())
                except getopt.GetoptError as erreur:
                    print(erreur)
                    sys.exit()
                except ValueError:
                    print('Les options entrées sont invalides')
                    sys.exit()
                try:
                    resultats = self.get_resultats(methodeCalc, leMot, nbSyn, self.matrice, self.indexes)
                    fin = time.time()
                    for i in range(0, int(nbSyn)):
                        print(i + 1, " : ", resultats[i][0], ", score = ", resultats[i][1])
                    print('\nAnalysé en {} secondes'.format(round((fin - debut), 2)))
                except KeyError as erreur:
                    print('Erreur de clé: ' + str(erreur))
                    print("Le mot n'existe peut-être pas dans le texte")
                except IndexError as erreur:
                    print("Erreur d'index: " + str(erreur))

    def trouver_cooccurrences(self):
        dico = {}
        tailleFenetre = self.fenetre // 2
        for i in range(len(self.liste_mots)):
            index_mot = self.indexes[self.liste_mots[i]]
            for j in range(1, tailleFenetre):
                if j != index_mot:
                    try:
                        tempIndex = self.indexes[self.liste_mots[i + j]]
                        if tempIndex <= index_mot:
                            cle = (tempIndex, index_mot, self.fenetre)
                            if cle not in dico:
                                dico[cle] = 1
                            else:
                                dico[cle] = dico[cle] + 1
                        tempIndex = self.indexes[self.liste_mots[i - j]]
                        if tempIndex <= index_mot:
                            cle = (tempIndex, index_mot, self.fenetre)
                            if cle not in dico:
                                dico[cle] = 1
                            else:
                                dico[cle] = dico[cle] + 1
                    except IndexError:
                        pass
        return dico

    def construire_matrice(self):
        taille_matrice = len(self.indexes)
        matrice_temp = np.zeros((taille_matrice, taille_matrice))
        matrice_reduite = self.bd.importer_matrice_bd(self.fenetre)
        for ligne, colonne, score in matrice_reduite:
            matrice_temp[ligne][colonne] = score
            matrice_temp[colonne][ligne] = score
        self.matrice = matrice_temp

    # Algorithme produit scalaire
    def produitScalaire(self, vector1, vector2):
        return np.dot(vector1, vector2)

    # Algorithme least-squares
    def leastSquare(self, vector1, vector2):
        return np.sum(np.square(np.subtract(vector1, vector2)))

    # Algorithme city-block
    def cityBlock(self, vector1, vector2):
        return np.sum(np.abs(np.subtract(vector1, vector2)))

    # Récupérer les données dans la BD
    def get_resultats(self, methodeCalc, leMot, nbSyn, matrice, indexes):
        resultats = self.algo(matrice, indexes, indexes[leMot], nbSyn, methodeCalc)
        return resultats

    def algo(self, matrice, dico_mot_vers_index, index_mot, nombre_resultats, method):
        score_dict = {}
        dico_index_vers_mot = {valeur: cle for cle, valeur in dico_mot_vers_index.items()}
        for i in range(matrice.shape[0]):
            if i != index_mot:
                if int(method) == 0:
                    score_dict[dico_index_vers_mot[i]] = self.produitScalaire(matrice[i], matrice[index_mot])
                elif int(method) == 1:
                    score_dict[dico_index_vers_mot[i]] = self.leastSquare(matrice[i], matrice[index_mot])
                elif int(method) == 2:
                    score_dict[dico_index_vers_mot[i]] = self.cityBlock(matrice[i], matrice[index_mot])
        return self.liste_resultats(nombre_resultats, self.trier_scores(True if method == 1 else False, score_dict))

    # Mot : Score
    def liste_resultats(self, nbResults, scores):
        listResults = []
        j = i = 0
        while j <= int(nbResults):
            if self.terminaison_et_stoplist(scores[i][0]):
                listResults.append([scores[i][0], scores[i][1]])
                j += 1
            i += 1
        return listResults

    # On enlève les mots qui auraient la même terminaison et on passe la stop list
    def terminaison_et_stoplist(self, mot):
        test = True
        if mot in self.retourner_stoplist() \
                or mot.endswith("ait") \
                or mot.endswith("ais") \
                or mot.endswith("aient") \
                or len(mot) < 2:
            test = False
        return test

    def retourner_stoplist(self):
        with open('stoplist.txt', mode='r', encoding="UTF-8") as handler:
            return handler.read().split(",")

    def trier_scores(self, rev, scoreDict):
        return sorted(scoreDict.items(), key=lambda k: k[1], reverse=rev)
