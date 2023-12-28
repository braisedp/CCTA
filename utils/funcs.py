import math


def q(HG, Q, elements):
    return Q * Gamma(HG, elements) / len(HG)


def Gamma(HG, elements):
    visited = {}
    for v in elements:
        for e in HG.FR[v]:
            visited[e] = True
    return list(visited.values()).count(True)


def top_k(collection, values, k):
    C = collection[:]
    for i in range(k):
        arg = i
        for ii in range(i, len(C)):
            if values[C[ii]] > values[C[arg]]:
                arg = ii
        C[i], C[arg] = C[arg], C[i]
    return C[:k]


def logcnk(n, k):
    res = 0
    for i in range(n - k + 1, n + 1):
        res += math.log(i)
    for i in range(1, k + 1):
        res -= math.log(i)
    return res
