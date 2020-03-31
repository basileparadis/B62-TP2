from DAO_BD import DAO_SQLite


class Controller:
    def __init__(self, arguments):
        self.argDict = dict.fromkeys(["verbose", "mode", "window", "encoding", "path", "drop", "clusterCount", "wordCount", "userCentroids"])
        self.arguments = arguments
        self.bd = DAO_SQLite()
        self.argDict["verbose"] = False

        self.wordList = None
        self.matrix = None
        self.indexes = None
        self.chrono = None