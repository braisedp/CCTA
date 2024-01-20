class HyperGraph:
    def __init__(self):
        self.edges = []
        self.RR = {}
        self.FR = {}
        self.length = 0

    def __len__(self):
        return self.length

    def add_edge(self, index, rr):
        self.RR[index] = rr
        self.edges.append(rr)
        self.length += 1

    def add_fr(self, v, index):
        if v in self.FR:
            self.FR[v].append(index)
        else:
            self.FR[v] = [index]

    def get_fr(self, v):
        if v in self.FR:
            return self.FR[v]
        return []
