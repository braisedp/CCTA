import math
from typing import List
from stable_matching.stableMatching import School, Student


def q(R, Q, elements):
    theta = len(R)
    count = 0
    for rr in R:
        I = 0
        for e in elements:
            if e.idx in rr:
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

    def __init__(self, budget, R, Q, D, costs):
        self.S = []
        self.A = []
        self.W = {}
        self.U = 0.0
        self.R = R
        self.Q = Q
        self.m_constraint = MatroidConstraint(budget, D, costs)
        self.r = self.m_constraint.r
        self.b_constraint = BudgetConstraint(budget, costs)

    def choice(self, worker):
        weight = q(self.R, self.Q, self.A + [worker]) - self.U
        if self.m_constraint.satisfy(self.S + [worker]):
            self.S.append(worker)
            self.A.append(worker)
            self.W[worker] = weight
            self.U += weight
        else:
            w_ = None
            min_ = math.inf
            for w in self.S:
                S_ = self.S.copy()
                S_.remove(w)
                S_.append(worker)
                if self.W[w] < min_ and self.m_constraint.satisfy(S_):
                    w_ = w
                    min_ = w
            if w_ is not None:
                if weight > self.r * self.W[w_]:
                    self.S.append(worker)
                    self.S.remove(w_)
                    self.A.append(worker)
                    self.W[worker] = weight
                    self.U += weight

    def select(self, workers: List):
        pass

    def preview(self, workers: List):
        pass

    def students(self) -> List:
        pass


class Worker(Student):
    def preview(self, schools: List):
        pass

    def preference_list(self):
        pass

    def propose(self) -> School:
        pass

    def rejected_by(self, school: School):
        pass

    def chosen_by(self, school: School):
        pass

    def school(self) -> School:
        pass

    def matched(self) -> bool:
        pass

    def prefer(self, school) -> bool:
        pass
