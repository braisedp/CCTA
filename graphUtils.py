import networkx
import random


def influence(G, S, Ep):
    F = []
    F += S
    for s in S:
        for i in range(0, len(G.neighbors(s))):
            if G.neighbors(s)[i] not in F:
                if random.random() > (1 - Ep[s, G.neighbors(s)[i]]):
                    F.append(G.neighbors(s)[i])
                else:
                    continue
    return F
