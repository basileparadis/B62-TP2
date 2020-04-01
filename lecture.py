import re


def televerser_fichier(chemin, encodage):
    file = open(chemin, mode='r', encoding=encodage)
    return file


def lire_texte(fichier):
    liste_mots = []
    for line in fichier.readlines():
        words = line.split()
        for word in words:
            word = normaliser(word)
            if word is not "":
                liste_mots.append(word)
    return liste_mots


def normaliser(mot):
    mot = mot.lower()
    mot = re.sub('.*\'', '', mot)
    mot = mot.translate({ord(c): None for c in ".,!?:;«»"})
    return mot


def liste_mots(chemin, encodage):
    return lire_texte(televerser_fichier(chemin, encodage))
