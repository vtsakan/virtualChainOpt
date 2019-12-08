class edgeDevice:
    def __init__(self, name, cpu):
        self.name = name;
        self.cpu = cpu;

    def getProcessingTime(self, load):
        return load/self.cpu;

    def getCost(self, load):
        return load**2 / self.cpu;

    def getName(self):
        return self.name;

    def getCPU(self):
        return self.cpu;
