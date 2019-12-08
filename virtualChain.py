class virtualChain:
    def __init__(self, name, fps):
        self.name = name;
        self.fps = fps;
        self.vflist = [];

    def addVF(self, VF):
        self.vflist.append(VF);

    def print(self):
        for vf in self.vflist:
            print(vf.getName(), '->', vf.getLoad());

    def getVFCHAIN(self):
        return self.vflist;

    def getVF(self, index):
        return self.vflist[index];

    def getQoS(self):
        return 1/self.fps;

    def deleteVF(self, vf):
        self.vflist.remove(vf);
