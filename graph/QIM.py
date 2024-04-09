import random
import math
import time

from graph.graph import generate_rr
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


def fu(C, R_1, k):
    min_val = math.inf
    for i in range(k + 1):
        S, f = node_selection_normal(C, R_1, i)
        min_val = min(f_u(C, S, f, R_1, k), min_val)
    return min_val


def sampling(graph, C, k, delta, epsilon, values, method='normal'):
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
    # print('i_max:{}'.format(i_max))
    # theta_0
    theta = 2 * math.pow(frac * math.sqrt(math.log(6 / delta)) + math.sqrt(frac * logcnk(n, k) + math.log(6 / delta)),
                         2)

    # print('Q:{},OPT:{},theta_max:{}'.format(Q, sum([values[e] for e in top_k(C, values, k)]),
    #                                         theta * math.pow(2, i_max)))

    for i in range(1, i_max):
        # start = time.time()
        delta1 = delta2 = delta / (3 * i_max)
        # generate reverse reachable set
        count = len(R_1)
        # processes = create_process(graph, values, R_1, R_2, count, theta - count, 8)
        # for p in processes:
        #     print(p.pid)
        # for p in processes:
        #     p.join()
        while count < theta:
            v1, v2 = random.choices(nodes, weights=values, k=2)
            generate_rr(graph, v1, R_1, index=count)
            generate_rr(graph, v2, R_2, index=count)
            count += 1
        # print('time of generating one rr:{}'.format(2*(time.time() - start)/theta))
        # time1 = time.time()
        # print('time1:{}'.format(time1 - start))
        Si, f = node_selection_normal(C, R_1, k)
        # time2 = time.time()
        # print('time2:{}'.format(time2 - time1))
        # lower bound of node selection
        sigma_l = math.pow(math.sqrt(Gamma(R_2, Si) + 2 * math.log(1 / delta2) / 9)
                           - math.sqrt(math.log(1 / delta2) / 2), 2) - math.log(1 / delta2) / 18
        # upper bound of optimum
        sigma_u = math.pow(math.sqrt(fu(C, R_1, k) + math.log(1 / delta1) / 2)
                           + math.sqrt(math.log(1 / delta1) / 2), 2)
        # print('time3:{}'.format(time.time() - time2))
        # print(sigma_l, sigma_u)
        if sigma_l / sigma_u >= 1 - 1 / math.e - epsilon:
            break
        theta *= 2
    return R_1


def generate_estimation(graph, values, count):
    nodes = range(graph.vcount())
    R = HyperGraph()
    num = 0
    while num < count:
        v = random.choices(nodes, weights=values, k=1)[0]
        generate_rr(graph, v, R, index=num)
        num += 1
    return R


# def node_selection_sq(C, R, k):
#     S = []
#     A = []
#     W = {}
#     U = 0.0
#     for s in C:
#         weight = Gamma(R, A + [s]) - U
#         if len(S) < k:
#             S.append(s)
#             A.append(s)
#             W[s] = weight
#             U += weight
#         else:
#             s_ = min(S, key=lambda x: W[x])
#             if weight > 2 * W[s_]:
#                 S.append(s)
#                 A.append(s)
#                 S.remove(s_)
#                 W[s] = weight
#                 U += weight
#     return S, Gamma(R, S)


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
