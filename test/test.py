import itertools
import math
import random
from utils.HyperGraph import HyperGraph
from stable_matching.TaskWorker import BChoice, MChoice
from utils.funcs import Gamma

n = 10
r = 30
elements = list(range(n))
R = HyperGraph(elements)
weights = [random.uniform(0.2, 0.6) for i in range(n)]
costs = {}
for i in range(n):
    costs[i] = weights[i]
for i in range(r):
    rr = random.sample(elements, random.randint(1, math.ceil(n / 2)))
    R.add_edge(i, rr)
    for v in rr:
        R.add_fr(v, i)

print(R.FR)
print(costs)

S = []
# choice_func = MChoice(S, R, 1.0, 4, costs)
choice_func = BChoice(S, R, 1.0,  costs)
queue = random.sample(elements, 5)
for e in queue:
    choice_func.choose(e)

max_gamma = 0
max_E = []

for i in range(len(queue)):
    for E in list(itertools.combinations(queue, i + 1)):
        gamma = Gamma(R, list(E))
        if gamma > max_gamma and sum([weights[i] for i in E]) < 1.0:
            max_E = list(E)
            max_gamma = gamma

print(max_E)
print(max_gamma)
print(S)
print(Gamma(R, S))
