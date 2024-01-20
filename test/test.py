import itertools
import math
import random
from utils.HyperGraph import HyperGraph
from stable_matching.TaskWorker import BChoice, MChoice, MaxCoverChoice
from utils.funcs import Gamma


class Element:
    def __init__(self, idx):
        self.idx = idx


n = 10
r = 30
elements = list(range(n))
R = HyperGraph(elements)
weights = [random.uniform(0.2, 0.6) for i in range(n)]
U = [Element(i) for i in elements]
costs = {}
for i in range(n):
    costs[U[i]] = weights[i]
for i in range(r):
    rr = random.sample(elements, random.randint(1, math.ceil(n / 2)))
    R.add_edge(i, rr)
    for v in rr:
        R.add_fr(v, i)

S = []
# choice_func = MChoice(S, R, 1.0, 4, costs)
choice_func = MaxCoverChoice(S, R, 1.0,  costs)
queue = random.sample(U, 5)
for e in queue:
    reject = choice_func.choose(e)
