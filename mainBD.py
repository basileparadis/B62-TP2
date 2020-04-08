"""
-------------------------------------
|       TP2 - B62 Projet Oracle     |
|           Basile Paradis          |
-------------------------------------
"""

import sys
from Controlleur import Controlleur

if __name__ == '__main__':
    controller = Controlleur(sys.argv)
    controller.process()


