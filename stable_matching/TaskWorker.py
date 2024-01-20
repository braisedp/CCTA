import itertools
import math
from typing import List
from stable_matching.stableMatching import School, Student
from utils.constraints import MatroidConstraint, BudgetConstraint
from utils.funcs import q, max_k


def gamma_workers(HG, workers):
    visited = {}
    for w in workers:
        for e in HG.get_fr(w.idx):
            visited[e] = True
    return list(visited.values()).count(True)


class MChoice:
    def __init__(self, S, R, budget, D, costs):
        self.R = R
        self.S = S
        self.A = []
        self.W = {}
        self.U = 0.0
        self.constraint = MatroidConstraint(budget, D, costs)
        self.r = 2.0

    def choose(self, worker):
        weight = gamma_workers(self.R, self.A + [worker]) - self.U
        if self.constraint.satisfy(self.S + [worker]):
            self.S.append(worker)
            self.A.append(worker)
            self.W[worker] = weight
            self.U += weight
            return []
        else:
            w_ = None
            min_ = math.inf
            for w in self.S:
                S_ = self.S.copy()
                S_.remove(w)
                S_.append(worker)
                if self.W[w] < min_ and self.constraint.satisfy(S_):
                    w_ = w
                    min_ = self.W[w]
            if w_ is not None:
                if weight > self.r * self.W[w_]:
                    self.S.append(worker)
                    self.S.remove(w_)
                    self.A.append(worker)
                    self.W[worker] = weight
                    self.U += weight
                    return [w_]
        return [worker]

    def refresh(self, S):
        self.S = S
        self.A = []
        self.W = {}
        self.U = 0.0


class BChoice:
    def __init__(self, S, HG, budget, costs):
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
            while v / cost > 2.0 * self.W[ordered_list[k]] / self.costs[ordered_list[k]]:
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

    def refresh(self, S):
        self.S = S
        self.A = []
        self.W = {}
        self.save = None
        self.save_frac = 1.0
        self.U = 0.0
        self.rest = self.budget


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
            if self.save is None:
                reject = []
                ordered_list = sorted(self.S, key=lambda e: self.Rhos[e], reverse=True)
                weight = 0.0
                k = 0
                while k < len(ordered_list):
                    weight += self.costs[ordered_list[k]]
                    if weight >= self.budget:
                        break
                    k += 1
                if weight <= self.budget:
                    return reject
                for w in ordered_list[k + 1:]:
                    self.S.remove(w)
                    reject.append(w)
                    for element in self.Z[w]:
                        self.z[element] -= self.Z[w][element]
                    self.Z.pop(w)
                w = ordered_list[k]
                if weight > self.budget:
                    self.S.remove(w)
                    reject.append(w)
                    x = 1.0 - (weight - self.budget) / self.costs[w]
                    for element in self.Z[w]:
                        self.z[element] -= (1.0 - x) * self.Z[w][element]
                        self.Z[w][element] = x * self.Z[w][element]
                    self.save = w
                    self.save_frac = x
                return reject

            else:
                reject = []
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
                for w in ordered_list[k + 1:]:
                    if w in self.S:
                        self.S.remove(w)
                        reject.append(w)
                    for element in self.Z[w]:
                        self.z[element] -= self.Z[w][element]
                    self.Z.pop(w)
                w = ordered_list[k]
                if weight > self.budget:
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
                        self.save = w
                        self.save_frac = x
                return reject
        return [worker]

    def refresh(self, S):
        self.S = S  # Solution
        self.save = None  # saved item
        self.save_frac = 1.0  # fraction of the saved item
        self.z = [0.0] * len(self.HG)  # fraction of all elements
        self.Z = {}  # fraction of all items on all elements
        self.Rhos = {}  # density of all items


class BSelect:
    def __init__(self, S, R, budget, costs):
        self.S = S
        self.R = R
        self.constraint = BudgetConstraint(budget, costs)

    def select(self, workers):
        S = []
        while True:
            v_max = 0
            v_e = None
            for e in workers:
                v = (gamma_workers(self.R, S + [e]) - gamma_workers(self.R, S)) / self.constraint.costs[e]
                if v > v_max:
                    v_max = v
                    v_e = e
            if v_e is not None and self.constraint.satisfy(S + [v_e]):
                S.append(v_e)
                workers.remove(v_e)
            else:
                break
        dispose = []
        for w in workers:
            if w in self.S:
                dispose.append(w)
        for s in self.S:
            if s not in S:
                self.S.remove(s)
        for s in S:
            self.S.append(s)
        return S, dispose

    def refresh(self, S):
        self.S = S


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

    def initialize(self, costs):
        self.costs = costs
        self.select_func = BSelect(self.S, self.R, self.budget, costs)

    def set_choice_matroid(self, D):
        self.choice_func = MChoice(self.S, self.R, self.budget, D, self.costs)

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

    def select(self, workers: List[Student]):
        # print('task:{},processing workers:{}'.format(self.id,[w.id for w in workers]))
        S, dispose = self.select_func.select(workers)
        for w in dispose:
            w.disposed()
            # print('dispose:{}'.format(w.id))
        for w in S:
            # print('select:{}'.format(w.id))
            w.selected_by(self)
        # print('S:{}'.format([w.id for w in self.S]))

    def preview(self, workers: List):
        pass

    def students(self) -> List:
        return self.S

    def dispose(self, worker):
        self.S.remove(worker)

    def refresh(self):
        self.S = []

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
        k = max_k(cost, costs)
        for i in range(k):
            for R in itertools.combinations(S, i + 1):
                A = list(set(S) - set(R))
                if sum([costs[e] for e in A]) + cost <= self.budget:
                    if gamma_workers(self.R, A + new) > gamma_workers(self.R, S):
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


class Worker(Student):
    def __init__(self, idx):
        self.task = None
        self.preference = None
        self.propose_list = None
        self.idx = idx

    def refresh(self):
        self.task = None
        self.propose_list = self.preference.copy()

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
        self.task = None

    def chosen_by(self, task):
        self.task = task

    def disposed(self):
        self.task = None

    def selected_by(self, task):
        if self.task is not None:
            # print('----remove from task:{}'.format(self.task.id))
            self.task.dispose(self)
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

    def __str__(self):
        return str(self.idx)


def outward_satisfactory(tasks, workers):
    total_matched_pairs = 0
    for task in tasks:
        total_matched_pairs += len(task.students())
    outward_unsatisfied_pairs = 0
    for task in tasks:
        for worker in workers:
            if worker.prefer(task) and task.prefer([worker]):
                outward_unsatisfied_pairs += 1
    return 1 - outward_unsatisfied_pairs / total_matched_pairs


def overall_satisfactory(tasks, workers):
    total_matched_pairs = 0
    for task in tasks:
        total_matched_pairs += len(task.students())
    overall_unsatisfied_pairs = 0
    for task in tasks:
        P = []
        visited = {}
        for worker in workers:
            visited[worker] = False
            if worker.prefer(task):
                P.append(worker)
        costs = {}
        for worker in P:
            costs[worker] = task.costs[worker]
        k = max_k(task.budget, costs)
        for i in range(k):
            for new in itertools.combinations(P, i + 1):
                if task.prefer(list(new)):
                    for worker in new:
                        if not visited[worker]:
                            overall_unsatisfied_pairs += 1
                            visited[worker] = True
    return 1 - overall_unsatisfied_pairs / total_matched_pairs


def individual_rationality_tasks(tasks):
    L = []
    for task in tasks:
        L.append([task.budget, sum(task.costs[e] for e in task.students())])
    return L


def average_utility_buyers(tasks):
    sum_utility = 0
    for task in tasks:
        sum_utility += q(task.HG, task.Q, task.students())
    return sum_utility / len(tasks)


def waste_pairwise(tasks, workers):
    wasted_pairs = 0
    total_matched_pairs = 0
    for task in tasks:
        total_matched_pairs += len(task.students())
    for task in tasks:
        for worker in workers:
            if worker.prefer(task) and task.have_vacancy_for([worker]):
                wasted_pairs += 1
    return wasted_pairs/total_matched_pairs
