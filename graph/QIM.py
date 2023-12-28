import random
import math
import time
from graph import generate_rr
from utils.funcs import Gamma, top_k, logcnk
from utils.HyperGraph import HyperGraph


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


def sampling(graph, C, k, delta, epsilon, values):
    nodes = list(graph.nodes)
    R_1 = HyperGraph(nodes)
    R_2 = HyperGraph(nodes)
    n = len(C)
    Q = sum(values)
    # worker_num = 8
    # workers = create_worker(graph, worker_num, values)
    i_max = math.ceil(math.log2(Q / (sum([values[e] for e in top_k(C, values, k)]) * math.pow(epsilon, 2))))
    theta = 2 * math.pow(1 / 4 * math.sqrt(math.log(6 / delta)) + math.sqrt(1 / 4 * logcnk(n, k) + math.log(6 / delta)),
                         2)
    print("imax ={},thetamax={}".format(i_max, theta * math.pow(i_max, 2)))
    for i in range(1, i_max):
        delta1 = delta2 = delta / (3 * i_max)
        start = time.time()

        # for ii in range(worker_num):
        #     workers[ii].inQ.put((theta - len(R_1)) / worker_num, len(R_1), ii)
        # for w in workers:
        #     R1_list, R2_list = w.outQ.get()
        #     R_1 += R1_list
        #     R_2 += R2_list

        count = 0
        while count < theta - len(R_1):
            l = random.choices(nodes, weights=values, k=2)
            v1, v2 = l[0], l[1]
            generate_rr(graph, v1, R_1, count)
            generate_rr(graph, v2, R_2, count)
            count += 1
        end1 = time.time()

        print('time to generate rr:{}'.format(end1 - start))
        Si, f = node_selection(C, R_1, k)
        print('node selection:{}'.format(time.time() - end1))

        sigma_l = math.pow(math.sqrt(Gamma(R_2, Si) + 2 * math.log(1 / delta2) / 9)
                           - math.sqrt(math.log(1 / delta2) / 2), 2) - math.log(1 / delta2) / 18
        sigma_u = math.pow(math.sqrt(f_u(C, Si, f, R_1, k) + math.log(1 / delta1) / 2)
                           + math.sqrt(math.log(1 / delta1) / 2), 2)
        # print(sigma_l / sigma_u)
        # print(len(R_1))
        if sigma_l / sigma_u >= 0.25:
            break
        theta *= 2
    # finish_worker(workers)
    return R_1


def node_selection(C, R, k):
    random.shuffle(C)
    S = []
    A = []
    W = {}
    U = 0.0
    for s in C:
        weight = Gamma(R, A + [s]) - U
        if len(S) < k:
            S.append(s)
            A.append(s)
            W[s] = weight
            U += weight
        else:
            s_ = min(S, key=lambda x: W[x])
            if weight > 2 * W[s_]:
                S.append(s)
                A.append(s)
                S.remove(s_)
                W[s] = weight
                U += weight
    return S, Gamma(R, S)


def QIM(graph, C, k, delta, epsilon, values):
    R = sampling(graph, C, k, delta, epsilon, values)
    Sk, z = node_selection(C, R, k)
    return Sk
