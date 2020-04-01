"""
-------------------------------------
|       TP2 - B62 Projet Oracle     |
|           Basile Paradis          |
-------------------------------------
"""

import sys
import getopt
import numpy as np
import re
import os


def main():
    # Lecture des arguments passés en ligne de commandes
    fichierTxt = tailleFenetre = None
    dictionnaire = {}
    mainFichierTxt = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'e:t:c:h', ['enc=', 'fenetre=', 'chemin=', 'help'])

        for opt, arg in opts:
            # Lire l'encodage
            if opt in ('-e', '--enc'):
                encodage = arg

            # Lire la taille de la fenêtre
            elif opt in ('-t', '--fenetre'):
                if arg.isnumeric():
                    tailleFenetre = arg
                else:
                    print("Taille de la fenêtre invalide")
                    sys.exit()

            # Lire le chemin relatif
            elif opt in ('-c', '--chemin'):
                chemin = arg
                if os.path.isfile(chemin):
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
                else:
                    print("Fichier texte introuvable")
                    sys.exit()

            # Afficher l'aide
            elif opt in ('-h', '--help'):
                print("Exemple: TP1.py -t 5 -e utf-8 -c ../test.txt")
                sys.exit()

        # Si les variables ne sont pas initialisées, on lance un message d'erreur, sinon on continue
        if tailleFenetre is None or fichierTxt is None:
            print("Arguments invalides (--help pour les indications)")
            sys.exit()
        else:
            print('\nEntrez un mot, le nombre de synonymes que vous voulez et la méthode de calcul.'
                  '\n\nProduit scalaire = 0, Least-Squares = 1, City-Block = 2, Quitter = "q"\n')

            saisie = input()
            if saisie == 'q':
                sys.exit()
            else:
                leMot, nbSyn, methodeCalc = saisie.split()

                matrice = remplirMatrice(mainFichierTxt, dictionnaire, {}, int(tailleFenetre))
                calculerScores(leMot, dictionnaire, matrice, methodeCalc)

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


if __name__ == '__main__':
    sys.exit(main())

stopWords = {"!": 0, "?": 0, "à": 0, "a": 0, "aussi": 0, "c": 0, "ça": 0, "car": 0, "ce": 0, "cela": 0, "ces": 0,
             "cette": 0, "ceux": 0, "cependant": 0, "chaque": 0, "ci": 0, "comme": 0, "comment": 0, "d": 0, "dans": 0,
             "de": 0, "des": 0, "du": 0, "dedans": 0, "dehors": 0, "depuis": 0, "devrait": 0, "doit": 0, "donc": 0,
             "dos": 0, "début": 0, "elle": 0, "elles": 0, "en": 0, "est": 0, "et": 0, "eu": 0, "fait": 0, "faites": 0,
             "font": 0, "hors": 0, "ici": 0, "il": 0, "ils": 0, "j": 0, "je": 0, "juste": 0, "l": 0, "la": 0, "le": 0,
             "les": 0, "leur": 0, "là": 0, "lui": 0, "lorsque": 0, "m": 0, "ma": 0, "me": 0, "maintenant": 0, "mais": 0,
             "mes": 0, "mine": 0, "moins": 0, "mon": 0, "mot": 0, "même": 0, "n": 0, "ne": 0, "ni": 0, "nommés": 0,
             "notre": 0, "nous": 0, "on": 0, "ou": 0, "où": 0, "par": 0, "parce": 0, "pas": 0, "peut": 0, "peu": 0,
             "plupart": 0, "pour": 0, "pourquoi": 0, "qu": 0, "quand": 0, "que": 0, "quel": 0, "quelle": 0,
             "quelles": 0, "quels": 0, "quelques": 0, "qui": 0, "s": 0, "sa": 0, "se": 0, "sans": 0, "ses": 0,
             "seulement": 0, "si": 0, "sien": 0, "son": 0, "sont": 0, "sous": 0, "soyez": 0, "sujet": 0, "sur": 0,
             "ta": 0, "tandis": 0, "tellement": 0, "tels": 0, "tes": 0, "ton": 0, "tu": 0, "un": 0, "une": 0,
             "votre": 0, "vous": 0, "vu": 0, "y": 0}
