class virtualChain:
    def __init__(self, name, fps):
        self.name = name;
        self.fps = fps;
        self.vflist = [];

    def addVF(self, VF):
        self.vflist.append(VF);

    def print(self):
        for vf in self.vflist:
            print(vf.getName());
