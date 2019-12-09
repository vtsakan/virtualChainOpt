class virtualFunction:
    def __init__(self, name, load, replica):
        self.name = name;
        self.load = load;
        self.replica = replica;

    def getName(self):
        return self.name;

    def getLoad(self):
        return self.load;

    def getReplica(self):
        return self.replica;
