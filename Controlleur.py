import argparse
import getopt
import os
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
        self.wordList = None
        self.matrix = None
        # sys.exit(main())

    def parse(self):
        parser = argparse.ArgumentParser(description='Cooccurences de mots dans un texte.')
        parser.add_argument('-e', action='store_true', help='mode entraînement')
        parser.add_argument('-t', '--fenetre', type=int, help='taille de la fenêtre', metavar='<taille>')
        parser.add_argument('--enc', help='encodage du fichier', metavar='<encodage>')
        parser.add_argument('-c', '--chemin', help='chemin du corpus d’entraînement', metavar='<chemin>')

        args = vars(parser.parse_args())

        entrainement = args['e']
        chemin = args['chemin']
        encodage = args['enc']
        fenetre = args['fenetre']

        self.process(entrainement, chemin, encodage, fenetre)

    def process(self, entrainement, chemin, encodage, fenetre):
        if entrainement is True and (chemin is None or encodage is None or fenetre is None):
            print('Vous devez définir -t --enc et --chemin')
            sys.exit()
        else:
            print(str(chemin) + ' ' + str(encodage) + ' ' + str(fenetre))

    def processArgParse(self):
        tailleFenetre = None
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'et:c:h', ['enc=', 'fenetre=', 'chemin=', 'help'])

            for opt, arg in opts:
                # Si on choisi le mode 'entraînement'
                if '-e' in sys.argv:
                    # Il faut que -t && --enc && --chemin soient définis pour l'entraînement
                    if '-t' and '--enc' and '--chemin' in sys.argv:
                        # TAILLE FENETRE
                        if opt in ('-t', '--fenetre'):
                            if arg.isnumeric():
                                tailleFenetre = arg
                            else:
                                print("Taille de la fenêtre invalide")
                                sys.exit()
                        # ENCODAGE
                        elif opt in ('--enc'):
                            encodage = arg
                        # CHEMIN RELATIF
                        elif opt in ('-c', '--chemin'):
                            if os.path.isfile(arg):
                                chemin = arg
                                '''
                                fichierTxt = open(chemin, 'r', encoding=encodage)
                                text = fichierTxt.read().lower()
                                for mots in re.findall('\w+|[!?]+', text):
                                    # Ajout de chaque mot à une liste qui contiendra le texte
                                    mainFichierTxt.append(mots)

                                    # Remplissage du dictionnaire de mot
                                    indexDict = 0
                                    if mots not in dictionnaire:
                                        dictionnaire[mots] = indexDict
                                        indexDict += 1
                                '''
                            else:
                                print("Fichier texte introuvable")
                                sys.exit()
                    else:
                        print("Vous devez fournir les options -t, --enc et --chemin, avec leurs arguments respectifs. ")
                        sys.exit()
                # AIDE
                elif opt in ('-h', '--help'):
                    print("Exemple: TP1.py -t 5 -e utf-8 -c ../test.txt")
                    sys.exit()
                else:
                    print("Vous devez choisir le mode (-e pour entraînement)")
                    sys.exit()

            # Si les variables ne sont pas initialisées, on lance un message d'erreur, sinon on continue
            if tailleFenetre is None or chemin is None:
                print("Arguments invalides (--help pour les indications)")
                sys.exit()
            else:
                print('\nEntrez un mot, le nombre de synonymes que vous voulez et la méthode de calcul.'
                      '\n\nProduit scalaire = 0, Least-Squares = 1, City-Block = 2, Quitter = "q"\n')

                saisie = input().lower()
                if saisie == 'q':
                    sys.exit()
                else:
                    leMot, nbSyn, methodeCalc = saisie.split()

                    listeMots = Lecture.liste_mots(chemin, encodage)
                    DAO_SQLite.inserer_dict(self.bd, listeMots)

                    # matrice = remplirMatrice(mainFichierTxt, dictionnaire, {}, int(tailleFenetre))
                    # calculerScores(leMot, dictionnaire, matrice, methodeCalc)

        except getopt.GetoptError as err:
            print(err)
            sys.exit()

    # Remplir la matrice de cooccurence en utilisant la fenêtre
    def remplirMatrice(texte, dictionnaire, matriceMot, tailleFenetre):
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
    def calculerScores(motRech, dictionnaire, matriceMot, algo):
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
    def produitScalaire(vector1, vector2):
        return np.dot(vector1, vector2)

    # Algorithme least-squares
    def leastSquare(vector1, vector2):
        return np.sum((vector1 - vector2) ** 2)

    # Algorithme city-block
    def cityBlock(vector1, vector2):
        return np.sum(np.abs(vector1 - vector2))
