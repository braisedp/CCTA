import random
import multiprocessing as mp
import math
from graph import generate_rr
from utils import Gamma


def top_k(collection, values, k):
    collection_ = sorted(collection, key=lambda x: values[x])
    return collection_[:k]


class Worker(mp.Process):
    def __init__(self, graph, values, inQ, outQ):
        super(Worker, self).__init__(target=self.start)
        self.graph = graph
        self.values = values
        self.inQ = inQ
        self.outQ = outQ
        self.R1 = []
        self.R2 = []
        self.count = 0

    def run(self):
        while True:
            theta = self.inQ.get()
            while self.count < theta:
                v1 = random.choices(list(self.graph.nodes), weights=self.values, k=1)[0]
                v2 = random.choices(list(self.graph.nodes), weights=self.values, k=1)[0]
                rr1 = generate_rr(self.graph, v1)
                rr2 = generate_rr(self.graph, v2)
                self.R1.append(rr1)
                self.R2.append(rr2)
                self.count += 1
            self.count = 0
            self.outQ.put((self.R1, self.R2))
            self.R1 = []
            self.R2 = []


def create_worker(graph, num, values):
    worker = []
    for i in range(num):
        # print(i)
        worker.append(Worker(graph, values, mp.Queue(), mp.Queue()))
        worker[i].start()
    return worker


def finish_worker(worker):
    for w in worker:
        w.terminate()


def sampling(graph, C, k, delta, epsilon, values):
    R_1 = []
    R_2 = []
    n = len(C)
    Q = sum(values)
    worker_num = 2
    workers = create_worker(graph, worker_num, values)
    i_max = math.ceil(math.log2(Q / (sum(top_k(C, values, k)) * math.pow(epsilon, 2))))
    theta = 2 * math.pow(1 / 4 * math.sqrt(math.log(6 / delta)) + math.sqrt(1 / 4 * logcnk(n, k) + math.log(6 / delta)),
                         2)
    for i in range(1, i_max):
        delta1 = delta2 = delta / (3 * i_max)
        for ii in range(worker_num):
            workers[ii].inQ.put((theta - len(R_1)) / worker_num)
        for w in workers:
            R1_list, R2_list = w.outQ.get()
            R_1 += R1_list
            R_2 += R2_list
        Si, f = node_selection(C, R_1, k)
        sigma_l = (math.pow(math.sqrt(Gamma(R_2, Si) + 2 * math.log(1 / delta2) / 9)
                            - math.sqrt(math.log(1 / delta2) / 2), 2) - math.log(1 / delta2) / 18)
        sigma_u = math.pow(math.sqrt(4 * Gamma(R_1, Si) + math.log(1 / delta1) / 2)
                           + math.sqrt(math.log(1 / delta1) / 2), 2)
        if sigma_l / sigma_u >= 0.25:
            break
        theta *= 2
    finish_worker(workers)
    return R_1


def node_selection(C, R, k):
    random.shuffle(C)
    S = []
    A = []
    W = {}
    for s in C:
        weight = Gamma(R, A + [s]) - Gamma(R, A)
        if len(S) < k:
            S.append(s)
            A.append(s)
            W[s] = weight
        else:
            s_ = min(S, key=lambda x: W[x])
            if weight > 2 * W[s_]:
                S.append(s)
                A.append(s)
                S.remove(s_)
                W[s] = weight
    return S, Gamma(R, S) / len(R)


def ctvm(graph, C, k, delta, epsilon, values):
    R = sampling(graph, C, k, delta, epsilon, values)
    Sk, z = node_selection(C, R, k)
    return Sk


def logcnk(n, k):
    res = 0
    for i in range(n - k + 1, n + 1):
        res += math.log(i)
    for i in range(1, k + 1):
        res -= math.log(i)
    return res
