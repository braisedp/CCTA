import itertools
import math
from typing import List

from graph.ISE import calculate_influence_quality
from stableMatching.School import School
from stableMatching.Student import Student
from utils.constraints import MatroidConstraint, BudgetConstraint
from utils.funcs import max_k


def gamma_workers(HG, workers):
    visited = {}
    for w in workers:
        for e in HG.get_fr(w.idx):
            visited[e] = True
    return list(visited.values()).count(True)


def calculate_influence_workers(workers, G, values):
    Sk = [worker.idx for worker in workers]
    return calculate_influence_quality(Sk, G, values)


def individual_rationality_tasks(tasks):
    L = []
    for task in tasks:
        L.append([task.budget, sum(task.costs[e] for e in task.students())])
    return L


class BChoice:
    def __init__(self, S, HG, budget, costs: dict):
        self.HG = HG  # Hyper Graph
        self.S = S  # Solution
        self.A = []  # Shadow Set
        self.save = None  # the only element : x<1
        self.save_frac = 1.0  # x
        self.W = {}  # v of all elements
        self.U = 0.0  # v(A)
        self.rest = budget  # budget left current
        self.budget = budget  # total budget
        self.costs = costs  # cost dict of all elements
        s_ = 0.0
        for cost in costs.values():
            if cost < budget:
                if cost / budget > s_:
                    s_ = cost / budget
        self.r = 2.0 - s_

    def choose(self, worker):
        v = gamma_workers(self.HG, [worker] + self.A) - self.U  # v(u)
        cost = self.costs[worker]  # w(u)
        # if insert u do not violate the budget constraint; in this case, rest >= 0 after insert u
        if self.rest >= cost:
            self.S.append(worker)
            self.A.append(worker)
            self.W[worker] = v
            self.rest = self.rest - cost
            self.U += v
            return []
        else:
            if self.save is not None:
                # if there exists one element with x < 1, in this case rest = 0 before insert u
                ordered_list = [self.save] + sorted(self.S, key=lambda e: self.W[e] / self.costs[e])
            else:
                # if all elements have x = 1, in this case rest >= 0 and rest < cost before insert u
                ordered_list = sorted(self.S, key=lambda e: self.W[e] / self.costs[e])
            # find min k such that sum(costs[i]|(i <= k)) + rest >= cost
            span = self.rest
            flag = False
            k = 0
            while v / cost > self.r * self.W[ordered_list[k]] / self.costs[ordered_list[k]]:
                if k == 0:
                    span += self.costs[ordered_list[k]] * self.save_frac
                else:
                    span += self.costs[ordered_list[k]]
                if span >= cost:
                    flag = True
                    break
                k += 1
            # if k exists, then remove 0,...,k from S
            if flag:
                reject = []
                if self.save is None:
                    self.S.remove(ordered_list[0])
                    reject.append(ordered_list[0])
                for i in range(1, k + 1):
                    self.S.remove(ordered_list[i])
                    reject.append(ordered_list[i])
                x = (span - cost) / self.costs[ordered_list[k]]
                # if x == 0, there is no saved element
                if x == 0.0:
                    self.save = None
                    self.save_frac = 1.0
                else:
                    # else, the lowest element doesn't belong to S, it is the saved element
                    self.save = ordered_list[k]
                    # x of the saved element is x
                    self.save_frac = x
                # after insert u, there is no budget left
                self.rest = 0.0
                # u is inserted
                self.S.append(worker)
                self.A.append(worker)
                self.W[worker] = v
                self.U += v
                return reject
        # if u is rejected, then worker and the saved element is rejected
        return [worker]


class MaxCoverChoice:
    def __init__(self, S, HG, budget, costs):
        self.HG = HG  # Hyper Graph
        self.S = S  # Solution
        self.save = None  # saved item
        self.save_frac = 1.0  # fraction of the saved item
        self.z = [0.0] * len(HG)  # fraction of all elements
        self.Z = {}  # fraction of all items on all elements
        self.Rhos = {}  # density of all items
        self.budget = budget  # total budget
        self.costs = costs  # cost dict of all elements

    def choose(self, worker):
        nodes = self.HG.get_fr(worker.idx)
        cost = self.costs[worker] / self.budget
        rho = 0.0
        for node in nodes:
            rho += 1.0 - self.z[node]
        rho /= cost
        if rho > 2.0 * sum(self.z):
            self.S.append(worker)
            self.Rhos[worker] = rho
            self.Z[worker] = {}
            for node in self.HG.get_fr(worker.idx):
                self.Z[worker][node] = 1.0 - self.z[node]
                self.z[node] = 1.0
            reject = []
            if self.save is None:
                ordered_list = sorted(self.S, key=lambda e: self.Rhos[e], reverse=True)
            else:
                ordered_list = sorted(self.S, key=lambda e: self.Rhos[e], reverse=True) + [self.save]
            weight = 0.0
            k = 0
            while k < len(ordered_list):
                if k == len(ordered_list) - 1:
                    weight += self.costs[ordered_list[k]] * self.save_frac
                else:
                    weight += self.costs[ordered_list[k]]
                if weight >= self.budget:
                    break
                k += 1
            if weight <= self.budget:
                return reject
            for w in ordered_list[k + 1:]:
                if w != self.save:
                    self.S.remove(w)
                    reject.append(w)
                for element in self.Z[w]:
                    self.z[element] -= self.Z[w][element]
                self.Z.pop(w)
            w = ordered_list[k]
            if w == self.save:
                x = self.save_frac - (weight - self.budget) / self.costs[w]
                for element in self.Z[w]:
                    self.z[element] = self.z[element] - (1.0 - x / self.save_frac) * self.Z[w][element]
                    self.Z[w][element] *= x / self.save_frac
                if x == 0.0:
                    self.Z.pop(w)
                    self.save = None
                    self.save_frac = 1.0
                else:
                    self.save_frac = x
            else:
                self.S.remove(w)
                reject.append(w)
                x = 1.0 - (weight - self.budget) / self.costs[w]
                for element in self.Z[w]:
                    self.z[element] = self.z[element] - (1.0 - x) * self.Z[w][element]
                    self.Z[w][element] = x * self.Z[w][element]
                if x == 0.0:
                    self.Z.pop(w)
                    self.save = None
                    self.save_frac = 1.0
                else:
                    self.save = w
                    self.save_frac = x
            return reject
        return [worker]


class BSelect:
    def __init__(self, R, budget, costs):
        self.R = R
        self.constraint = BudgetConstraint(budget, costs)
        self.costs = costs

    def select(self, workers):
        S = []
        while self.constraint.satisfy(S) and len(workers) > 0:
            V = {}
            for worker in workers:
                if self.constraint.satisfy(S+[worker]):
                    V[worker] = gamma_workers(self.R, S+[worker])-gamma_workers(self.R, S)
                else:
                    V[worker] = 0
            v_e = max(workers, key=lambda x: V[x]/self.costs[x])
            if self.constraint.satisfy(S + [v_e]):
                S.append(v_e)
            workers.remove(v_e)
        return S


class Task(School):
    def __init__(self, idx, budget, R, Q):
        self.idx = idx
        self.choice_func = None
        self.select_func = None
        self.costs = None
        self.budget = budget
        self.S = []
        self.R = R
        self.Q = Q
        self.es_RR = None
        self. v = 0.0

    def initialize(self, costs):
        self.costs = costs
        self.select_func = BSelect(self.R, self.budget, costs)

    def set_choice_budget(self):
        self.choice_func = BChoice(self.S, self.R, self.budget, self.costs)

    def set_choice_max_cover(self):
        self.choice_func = MaxCoverChoice(self.S, self.R, self.budget, self.costs)

    def choice(self, worker: Student):
        if self.costs[worker] <= self.budget:
            reject = self.choice_func.choose(worker)
        else:
            reject = [worker]
        if worker in self.S:
            worker.chosen_by(self)
        for r in reject:
            r.rejected_by(self)

    def select(self, workers: list):
        # print(self)
        S = self.select_func.select(workers.copy())
        if gamma_workers(self.R, S) > gamma_workers(self.R, self.S):
            dispose = set(self.S)-set(S)
            # print('dispose:{}'.format([d.idx for d in dispose]))
            for w in dispose:
                self.dispose(w)
                w.disposed()
            # print('pre select:{}'.format([s.idx for s in self.S]))
            for w in S:
                w.selected_by(self)
            self.S = S
            # print('S:{}'.format([w.id for w in self.S]))

    def preview(self, workers: List):
        pass

    def students(self) -> List:
        return self.S

    def dispose(self, worker):
        self.S.remove(worker)
        worker.disposed()

    def refresh(self):
        self.S = []
        self.v = 0

    def prefer(self, new):
        S = self.S
        costs = {}
        used = 0.0
        for worker in S:
            costs[worker] = self.costs[worker]
            used += costs[worker]
        cost = sum([self.costs[i] for i in new])
        if cost > self.budget:
            return False
        if cost <= self.budget - sum([costs[e] for e in S]):
            return True
        k = max_k(self.budget-cost, costs)
        if gamma_workers(self.es_RR, new) > gamma_workers(self.es_RR, S):
            return True
        for i in range(k):
            for A in itertools.combinations(S, k-i):
                A = list(A)
                if sum([costs[e] for e in A]) + cost <= self.budget:
                    if gamma_workers(self.es_RR, A + new) > gamma_workers(self.es_RR, S):
                        return True
        return False

    def have_vacancy_for(self, new):
        S = self.S
        costs = {}
        used = 0.0
        for worker in S:
            costs[worker] = self.costs[worker]
            used += costs[worker]
        cost = sum([self.costs[i] for i in new])
        if cost + used <= self.budget:
            return True
        return False

    def __str__(self):
        return str(self.idx)

    def set_estimation_rr(self, RR):
        self.es_RR = RR
