import random
import multiprocessing as mp
import time
import math
from graph import generate_rr
from utils.funcs import logcnk


class Worker(mp.Process):
    def __init__(self, graph, inQ, outQ):
        super(Worker, self).__init__(target=self.start)
        self.graph = graph
        self.inQ = inQ
        self.outQ = outQ
        self.R = []
        self.count = 0

    def run(self):

        while True:
            theta = self.inQ.get()
            # print(theta)
            while self.count < theta:
                v = random.choice(list(self.graph.nodes))
                rr = generate_rr(self.graph, v)
                self.R.append(rr)
                self.count += 1
            self.count = 0
            self.outQ.put(self.R)
            self.R = []


def create_worker(graph, num):
    worker = []
    for i in range(num):
        # print(i)
        worker.append(Worker(graph, mp.Queue(), mp.Queue()))
        worker[i].start()
    return worker


def finish_worker(worker):
    for w in worker:
        w.terminate()


def sampling(graph, k, epsilon, l):
    R = []
    LB = 1
    n = len(graph.nodes)
    epsilon_p = epsilon * math.sqrt(2)
    worker_num = 8
    worker = create_worker(graph, worker_num)
    for i in range(1, int(math.log2(n - 1)) + 1):
        s = time.time()
        x = n / (math.pow(2, i))
        lambda_p = ((2 + 2 * epsilon_p / 3) * (logcnk(n, k) + l * math.log(n) + math.log(math.log2(n))) * n) / pow(
            epsilon_p, 2)
        theta = lambda_p / x
        for ii in range(worker_num):
            worker[ii].inQ.put((theta - len(R)) / worker_num)
        for w in worker:
            R_list = w.outQ.get()
            R += R_list
        # count = 0
        # print('theta={}'.format(theta))
        # while count < theta:
        #     v = random.randint(0, len(graph.nodes) - 1)
        #     rr = generate_rr(graph, v)
        #     print('count:{}'.format(count))
        #     R.append(rr)
        #     count += 1
        print('time to find rr', time.time() - s)
        start = time.time()
        Si, f = node_selection(graph, R, k)
        print(f)
        print('node selection time', time.time() - start)
        if n * f >= (1 + epsilon_p) * x:
            LB = n * f / (1 + epsilon_p)
            break
    alpha = math.sqrt(l * math.log(n) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e) * (logcnk(n, k) + l * math.log(n) + math.log(2)))
    lambda_aster = 2 * n * pow(((1 - 1 / math.e) * alpha + beta), 2) * pow(epsilon, -2)
    theta = lambda_aster / LB
    length_r = len(R)
    diff = theta - length_r
    _start = time.time()
    if diff > 0:
        for ii in range(worker_num):
            worker[ii].inQ.put(diff / worker_num)
        for w in worker:
            R_list = w.outQ.get()
            R += R_list
    '''
    
    while length_r <= theta:
        v = random.randint(1, n)
        rr = generate_rr(v)
        R.append(rr)
        length_r += 1
    '''
    _end = time.time()
    print(_end - _start)
    finish_worker(worker)
    return R


def node_selection(graph, R, k):
    Sk = set()
    rr_degree = [0] * (len(graph.nodes) + 1)
    node_rr_set = dict()
    matched_count = 0
    for j in range(0, len(R)):
        rr = R[j]
        for rr_node in rr:
            rr_degree[rr_node] += 1
            if rr_node not in node_rr_set:
                node_rr_set[rr_node] = list()
            node_rr_set[rr_node].append(j)
    for i in range(k):
        max_point = rr_degree.index(max(rr_degree))
        Sk.add(max_point)
        matched_count += len(node_rr_set[max_point])
        index_set = []
        for node_rr in node_rr_set[max_point]:
            index_set.append(node_rr)
        for jj in index_set:
            rr = R[jj]
            for rr_node in rr:
                rr_degree[rr_node] -= 1
                node_rr_set[rr_node].remove(jj)
    return Sk, matched_count / len(R)


def imm(graph, k, episode, l):
    n = len(graph.nodes)
    l = l * (1 + math.log(2) / math.log(n))
    R = sampling(graph, k, episode, l)
    Sk, z = node_selection(graph, R, k)
    return Sk
