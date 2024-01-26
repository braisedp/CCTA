import random
import networkx as nx
from utils.HyperGraph import HyperGraph
import pandas as pd
import numpy as np


def read_graph(filename, directed=False):
    if not directed:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    with open(filename) as f:
        for line in f:
            words = line.split(',')
            e0 = int(words[0])
            e1 = int(words[1])
            try:
                G[e0][e1]["weight"] += 1
            except KeyError:
                G.add_edge(e0, e1, weight=1)
    return G


def read_graph_with_weights(filename, directed=False):
    if not directed:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    with open(filename) as f:
        for line in f:
            words = line.split()
            e0 = int(words[0])
            e1 = int(words[1])
            w = float(words[2])
            G.add_edge(e0, e1, weight=w)
    return G


def read_graph_without_weights(filename, directed=False):
    if not directed:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    with open(filename) as f:
        for line in f:
            e0, e1 = map(int, line.split())
            G.add_edge(e0, e1)
    return G


def read_graph_from_csv(filename, task, directed=False):
    if not directed:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    df = pd.read_csv(filename)
    for i in range(len(df)):
        data = df.iloc[i, [1, 2, task + 3]]
        G.add_edge(int(data.iloc[0]), int(data.iloc[1]), weight=float(data.iloc[2]))
    return G


def convert_undirected_to_directed(G):
    assert G.isinstance(type(nx.Graph()))
    # check if there are weights on edges
    e1, e2 = G.edges()[0]
    if "weight" in G[e1][e2]:
        weighted = True
    else:
        weighted = False
    directed_G = nx.DiGraph()
    if weighted:
        for e in G.edges():
            directed_G.add_weighted_edges_from(
                [(e[0], e[1], G[e[0]][e[1]]["weight"]), (e[1], e[0], G[e[1]][e[0]]["weight"])])
    else:
        for e in G.edges():
            directed_G.add_edges_from([(e[0], e[1]), (e[1], e[0])])
    return directed_G


def read_adjacency_list(filename, directed=False):
    if not directed:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    with open(filename) as f:
        for node, line in enumerate(f):
            neighbors = map(int, line.split())
            G.add_node(node)
            G.add_edges_from([(node, v) for v in neighbors])
    return G


def gen_prb(n, mu, sigma, lower=0, upper=1):
    import scipy.stats as stats
    X = stats.truncnorm(
        (lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
    return X.rvs(n)


def wrt_prb(i_flnm, o_flnm, mu=0.09, sigma=0.06, undirected=True):
    G = read_graph(i_flnm)
    m = len(G.edges())
    X = gen_prb(m, mu, sigma)
    with open(o_flnm, "w+") as f:
        for i, e in enumerate(G.edges()):
            f.write("%d %d %s\n" % (e[0], e[1], X[i]))
            if undirected:
                f.write("%d %d %s\n" % (e[1], e[0], X[i]))


def wrt_prb_tasks(i_flnm, o_flnm, n, mu=0.1, sigma=0.05, directed=False):
    G = read_graph(i_flnm)
    m = len(G.edges())
    print(m)
    o_nodes = [e[0] for e in G.edges]
    i_nodes = [e[1] for e in G.edges]
    if not directed:
        o_nodes += [e[1] for e in G.edges]
        i_nodes += [e[0] for e in G.edges]
    df = pd.DataFrame({'from': o_nodes, 'to': i_nodes})
    for i in range(n):
        prb = np.array(gen_prb(m, mu=mu, sigma=sigma))
        if not directed:
            prb = np.tile(prb, 2)
        df.insert(loc=2 + i, column='{}'.format(i), value=prb)
    print(len(df))
    df.to_csv(o_flnm)


def generate_rr(graph, v, HG: HyperGraph, index):
    return generate_rr_ic(graph, v, HG, index)


def generate_rr_ic(graph, node, HG: HyperGraph, index):
    activity_set = list()
    activity_set.append(node)
    activity_nodes = list()
    activity_nodes.append(node)
    while activity_set:
        new_activity_set = list()
        for seed in activity_set:
            for v in graph.neighbors(seed):
                weight = graph[seed][v]['weight']
                if v not in activity_nodes:
                    if random.random() < weight:
                        HG.add_fr(v, index)
                        activity_nodes.append(v)
                        new_activity_set.append(v)
        activity_set = new_activity_set
    HG.add_edge(index, activity_nodes)
