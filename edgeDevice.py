class edgeDevice:
    def __init__(self, name, cpu):
        self.name = name;
        self.cpu = cpu;

    def processingTime(self, load):
        return load/self.cpu;

    def cost(self, load):
        return load**2 / self.cpu;
