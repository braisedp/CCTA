class HyperGraph:
    def __init__(self, elements):
        self.elements = elements
        self.edges = []
        self.RR = {}
        self.FR = {}
        self.length = 0
        for e in elements:
            self.FR[e] = []

    def __len__(self):
        return self.length

    def addEdge(self, index, rr):
        self.RR[index] = rr
        self.edges.append(rr)
        self.length += 1

    def addFR(self, v, index):
        self.FR[v].append(index)

    def __add__(self, HG2):
        HG = HyperGraph(self.elements)
        HG.edges = self.edges + HG2.edges
        HG.RR.update(self.RR)
        HG.RR.update(HG2.RR)
        for key in self.FR:
            HG.FR[key] = self.FR[key] + HG2.FR[key]
        HG.length = self.length + HG2.length
        return HG
