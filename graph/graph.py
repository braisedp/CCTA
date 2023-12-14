import networkx as nx


def read_graph(filename, directed=False):
    if not directed:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    with open(filename) as f:
        for line in f:
            e0, e1= map(int, line.split())
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
            l = line.split()
            e0 = int(l[0])
            e1 = int(l[1])
            w = float(l[2])
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


def wrt_prb(i_flnm, o_flnm, mu=0.09, sigma=0.06, directed=True):
    G = read_graph(i_flnm)
    m = len(G.edges())
    X = gen_prb(m, mu, sigma)
    with open(o_flnm, "w+") as f:
        for i, e in enumerate(G.edges()):
            f.write("%d %d %s\n" % (e[0], e[1], X[i]))
            if directed:
                f.write("%d %d %s\n" % (e[1], e[0], X[i]))
