import random
import networkx as nx
import igraph as ig
from utils.HyperGraph import HyperGraph
import pandas as pd
import numpy as np


def read_graph(filename, wcol=-1, sep=',', directed=True):
    df = pd.read_csv(filename, sep=sep)

    # 提取边和权重
    edges = list(zip(df['from'], df['to']))

    # 创建有向图
    graph = ig.Graph(directed=directed)

    nodes = set(sum(edges, ()))

    # 添加节点和边
    graph.add_vertices(len(nodes))  # 添加所有节点
    graph.add_edges(edges)  # 添加边

    if wcol >= 0:
        weights = df['{}'.format(wcol)].tolist()
        graph.es['weight'] = weights

    return graph


def read_graphs(filename, cols, sep=',',directed=True):
    df = pd.read_csv(filename, sep=sep)
    edges = list(zip(df['from'], df['to']))
    graphs = []
    nodes = set(sum(edges, ()))
    for col in cols:
        graph = ig.Graph(directed=directed)
        graph.add_vertices(len(nodes))  # 添加所有节点
        graph.add_edges(edges)  # 添加边
        weights = df['{}'.format(col)].tolist()
        graph.es['weight'] = weights
        graphs.append(graph)
    return graphs


def gen_prb(n, mu, sigma):
    import scipy.stats as stats
    lower = mu-2*sigma
    upper = mu+2*sigma
    X = stats.truncnorm(
        (lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
    return X.rvs(n)


def wrt_prb_tasks(i_flnm, o_flnm, n, sep=',', start=0, mu=0.1, sigma=0.05, directed=True):
    G = read_graph(i_flnm, sep=sep, directed=directed)
    m = len(G.es())
    df = pd.read_csv(o_flnm)
    cols = {}
    for i in range(n):
        prb = np.array(gen_prb(m, mu=mu, sigma=sigma))
        cols['{}'.format(i+start)] = prb
    new_df = pd.DataFrame(cols)
    df = pd.concat([df, new_df], axis=1)
    df.to_csv(o_flnm, index=False)


def gen_prb_uniform(n):
    import scipy.stats as stats
    X = stats.uniform(0.1, 0.5)
    return X.rvs(n)


def wrt_prb_tasks_uniform(i_flnm, o_flnm, n, sep=',', start=0, directed=True):
    G = read_graph(i_flnm, sep=sep, directed=directed)
    m = len(G.es())
    df = pd.read_csv(o_flnm)
    cols = {}
    for i in range(n):
        prb = np.array(gen_prb_uniform(m))
        cols['{}'.format(i + start)] = prb
    new_df = pd.DataFrame(cols)
    df = pd.concat([df, new_df], axis=1)
    df.to_csv(o_flnm, index=False)


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
            for e in graph.vs[seed].in_edges():
                v = e.source
                weight = e['weight']
                if v not in activity_nodes:
                    if random.random() < weight:
                        HG.add_fr(v, index)
                        activity_nodes.append(v)
                        new_activity_set.append(v)
        activity_set = new_activity_set
    HG.add_edge(index, activity_nodes)
    return len(activity_nodes)
