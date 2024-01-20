import itertools
import math
import random
from utils.HyperGraph import HyperGraph
from stable_matching.TaskWorker import BChoice, MChoice, MaxCoverChoice, gamma_workers
from utils.funcs import Gamma


class Element:
    def __init__(self, idx):
        self.idx = idx

    def __str__(self):
        return str(self.idx)


n = 10
r = 20
elements = list(range(n))
R = HyperGraph()
weights = [random.uniform(0.2, 0.6) for i in range(n)]
U = [Element(i) for i in elements]
costs = {}
for i in range(n):
    costs[U[i]] = weights[i]
for i in range(r):
    rr = random.sample(elements, random.randint(1, math.ceil(n / 4)))
    R.add_edge(i, rr)
    for v in rr:
        R.add_fr(v, i)

S = []
choice_func1 = BChoice(S, R, 1.0, costs)
S_ = []
choice_func2 = MaxCoverChoice(S_, R, 1.0,  costs)
queue = random.sample(U, 8)
for e in queue:
    choice_func1.choose(e)
    choice_func2.choose(e)

print(gamma_workers(R, S))
print(gamma_workers(R, S_))


