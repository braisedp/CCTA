import random
import math
import time

from graph.graph import generate_rr
from utils.funcs import Gamma, top_k, logcnk
from utils.HyperGraph import HyperGraph
import multiprocessing as mp


class Worker(mp.Process):
    def __init__(self, outQ, graph, nodes, values, first, count):
        super(Worker, self).__init__(target=self.start)
        self.graph = graph
        self.nodes = nodes
        self.values = values
        self.count = count
        self.first = first
        self.outQ = outQ

    def run(self):
        R = HyperGraph()
        while self.count > 0:
            v = random.choices(self.nodes, weights=self.values, k=1)
            generate_rr(self.graph, v[0], R, index=self.first + self.count)
            self.count -= 1

        self.outQ.put(R)


def create_worker(num, graph, nodes, values, start, count):
    worker = []
    for i in range(num):
        worker.append(Worker(mp.Queue(), graph=graph, nodes=nodes, values=values, first=start + i * count
                             , count=count))
        worker[i].start()
    return worker


def finish_worker(worker):
    for w in worker:
        w.terminate()


def f_u(C, Si, f, R_1, k):
    V = {}
    for e in C:
        if e not in Si:
            V[e] = Gamma(R_1, Si + [e]) - f
    S = top_k(list(V.keys()), V, k)
    val = f
    for e in S:
        val += V[e]
    return val


def fu(C, R_1, k):
    min_val = math.inf
    for i in range(k + 1):
        S, f = node_selection_normal(C, R_1, i)
        min_val = min(f_u(C, S, f, R_1, k), min_val)
    return min_val


def sampling(graph, C, k, delta, epsilon, values, method='normal', processes=1):
    nodes = range(graph.vcount())
    R_1 = HyperGraph()
    R_2 = HyperGraph()
    n = len(C)
    Q = sum(values.values())
    if method == 'normal':
        frac = 1.0 - 1.0 / math.sqrt(math.e)
    else:
        frac = 1 / 4
    i_max = math.ceil(math.log2(Q / (sum([values[e] for e in top_k(C, values, k)]) * math.pow(epsilon, 2))))
    theta = 2 * math.pow(frac * math.sqrt(math.log(6 / delta)) + math.sqrt(frac * logcnk(n, k) + math.log(6 / delta)),
                         2)
    for i in range(1, i_max):
        delta1 = delta2 = delta / (3 * i_max)
        # generate reverse reachable set
        count = len(R_1)
        if processes == 1:
            while count < theta:
                v1, v2 = random.choices(nodes, weights=values, k=2)
                generate_rr(graph, v1, R_1, index=count)
                generate_rr(graph, v2, R_2, index=count)
                count += 1
        else:
            worker1 = create_worker(num=processes, graph=graph, nodes=nodes, values=values,
                                    start=count, count=(int(theta)-count)//processes)
            worker2 = create_worker(num=processes, graph=graph, nodes=nodes, values=values,
                                    start=count, count=(int(theta) - count) // processes)
            for w in worker1:
                R1 = w.outQ.get()
                R_1.merge(R1)
            for w in worker2:
                R2 = w.outQ.get()
                R_2.merge(R2)
            finish_worker(worker1)
            finish_worker(worker2)
        Si, f = node_selection_normal(C, R_1, k)
        # lower bound of node selection
        sigma_l = math.pow(math.sqrt(Gamma(R_2, Si) + 2 * math.log(1 / delta2) / 9)
                           - math.sqrt(math.log(1 / delta2) / 2), 2) - math.log(1 / delta2) / 18
        # upper bound of optimum
        sigma_u = math.pow(math.sqrt(fu(C, R_1, k) + math.log(1 / delta1) / 2)
                           + math.sqrt(math.log(1 / delta1) / 2), 2)
        if sigma_l / sigma_u >= 1 - 1 / math.e - epsilon:
            break
        theta *= 2
    return R_1


def generate_estimation(graph, values, count, processes=1):
    nodes = range(graph.vcount())
    R = HyperGraph()
    num = 0
    if processes == 1:
        while num < count:
            v = random.choices(nodes, weights=values, k=1)[0]
            generate_rr(graph, v, R, index=num)
            num += 1
    else:
        worker = create_worker(num=processes, graph=graph, nodes=nodes, values=values, start=0, count=count//processes)
        for w in worker:
            R_ = w.outQ.get()
            R.merge(R_)
        finish_worker(worker)
    return R


def node_selection_normal(C, R, k):
    S = []
    U = 0.0
    N = C.copy()
    for _ in range(k):
        n = max(N, key=lambda x: Gamma(R, S + [x]) - U)
        N.remove(n)
        S.append(n)
        U = Gamma(R, S + [n])
    return S, U

# def QIM(graph, C, k, delta, epsilon, values):
#     R = sampling(graph, C, k, delta, epsilon, values)
#     Sk, z = node_selection_sq(C, R, k)
#     return Sk
