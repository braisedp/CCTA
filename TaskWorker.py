import math
from typing import List
from stable_matching.stableMatching import School, Student


def q(R, Q, elements):
    theta = len(R)
    count = 0
    for rr in R:
        I = 0
        for e in elements:
            if e in rr:
                I = 1
                break
        count += I
    return Q * count / theta


class MatroidConstraint:
    def __init__(self, budget: float, D: int, costs: dict):
        s_ = 0.0
        for cost in costs.values():
            if cost < budget:
                if cost / budget > s_:
                    s_ = cost / budget
        gamma = math.ceil(1 + math.log(D) / (1 - s_))
        self.costs = costs
        self.bounds = []
        self.bounds.append(budget)
        for i in range(1, D + 1):
            self.bounds.append(budget / (i * gamma))
        self.r = 1 + math.sqrt(1 / gamma)

    def satisfy(self, elements):
        l = sorted(elements, key=lambda x: self.costs[x], reverse=True)
        if len(l) > len(self.bounds):
            return False
        for i in range(len(l)):
            if self.costs[l[i]] >= self.bounds[i]:
                return False
        return True


class BudgetConstraint:
    def __init__(self, budget: float, costs: dict):
        self.costs = costs
        self.budget = budget

    def satisfy(self, elements):
        total = 0
        for w in elements:
            total += self.costs[w]
        return total <= self.budget


class Task(School):

    def __init__(self, ID, budget, R, Q):
        self.id = ID
        self.b_constraint = None
        self.r = None
        self.costs = None
        self.m_constraint = None
        self.S = []
        self.A = []
        self.W = {}
        self.R = R
        self.Q = Q
        self.budget = budget

    def refresh(self):
        self.S = []
        self.A = []
        self.W = {}

    def set_costs(self, costs, D):
        self.costs = costs
        self.m_constraint = MatroidConstraint(self.budget, D, costs)
        self.r = self.m_constraint.r
        self.b_constraint = BudgetConstraint(self.budget, costs)

    def choice(self, worker):
        weight = q(self.R, self.Q, self.A + [worker]) - q(self.R, self.Q, self.A)
        if self.m_constraint.satisfy(self.S + [worker]):
            self.S.append(worker)
            self.A.append(worker)
            self.W[worker] = weight
            worker.chosen_by(self)
            return
        else:
            w_ = None
            min_ = math.inf
            for w in self.S:
                S_ = self.S.copy()
                S_.remove(w)
                S_.append(worker)
                if self.W[w] < min_ and self.m_constraint.satisfy(S_):
                    w_ = w
                    min_ = self.W[w]
            if w_ is not None:
                if weight > self.r * self.W[w_]:
                    self.S.append(worker)
                    self.S.remove(w_)
                    w_.rejected_by(self)
                    self.A.append(worker)
                    self.W[worker] = weight
                    worker.chosen_by(self)
                    return
        worker.rejected_by(self)

    def select(self, workers: List):
        S = []
        while True:
            v_max = 0
            v_e = None
            for e in workers:
                v = (q(self.R, self.Q, S + [e])-q(self.R, self.Q, S)) / self.b_constraint.costs[e]
                if v > v_max:
                    v_max = v
                    v_e = e
            if v_e is not None and self.b_constraint.satisfy(S + [v_e]):
                S.append(v_e)
                workers.remove(v_e)
            else:
                break
        for w in workers:
            if w in self.S:
                w.task = None
        for w in S:
            if w.task is not None:
                w.task.S.remove(w)
            w.task = self
        self.S = S

    def preview(self, workers: List):
        pass

    def students(self) -> List:
        return self.S


class Worker(Student):

    def __init__(self, ID):
        self.task = None
        self.preference = None
        self.id = ID
        self.propose_list = None

    def refresh(self):
        self.task = None

    def set_preference(self, values):
        self.preference = sorted(values.keys(), key=lambda x: values[x], reverse=True)
        self.propose_list = self.preference.copy()

    def preview(self, schools: List):
        pass

    def preference_list(self):
        return self.preference

    def propose(self):
        return self.propose_list[0]

    def rejected_by(self, task):
        self.propose_list.remove(task)

    def chosen_by(self, task):
        self.task = task

    def school(self):
        return self.task

    def matched(self) -> bool:
        if self.task is not None or len(self.propose_list) == 0:
            return True
        return False

    def prefer(self, task) -> bool:
        if task is None:
            return False
        if self.task is None:
            return True
        return self.preference.index(task) < self.preference.index(self.task)
