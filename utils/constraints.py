import math


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
