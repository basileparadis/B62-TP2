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
            if word != "":
                liste_mots.append(word)
    return liste_mots


def normaliser(mot):
    # Mettre les mots en minuscule
    mot = mot.lower()
    # Enlever les apostrophes
    mot = re.sub('.*\'', '', mot)
    # Enlever toute ponctuation/caractère spécial
    mot = mot.translate({ord(carac): None for carac in "«»':;,.?!"})
    return mot


def liste_mots(chemin, encodage):
    return lire_texte(televerser_fichier(chemin, encodage))
