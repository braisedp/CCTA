import networkx as nx
import random
import time
import re
from copy import deepcopy


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


def gen_prb (n, mu, sigma, lower=0, upper=1):
    '''Generate probability from normal distribution in the range [0,1].
    '''
    import scipy.stats as stats
    X = stats.truncnorm(
         (lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
    return X.rvs(n)

def read_graph(filename, directed=False):
    if not directed:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    with open(filename) as f:
        for line in f:
            e0, e1 = map(int, line.split())
            G.add_edge(e0, e1)
    return G


def generate_graph(filename, directed=False):
    start = time.time()

    G = read_graph(filename, directed=False)

    print('reading graph')
    print('time-used:{t:.2f}'.format(t=time.time() - start))


