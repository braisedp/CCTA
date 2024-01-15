import itertools
import math
from typing import List
from stable_matching.stableMatching import School, Student
from utils.constraints import MatroidConstraint, BudgetConstraint
from utils.funcs import Gamma, q


class MChoice:
    def __init__(self, S, R, budget, D, costs):
        self.R = R
        self.S = S
        self.A = []
        self.W = {}
        self.U = 0.0
        self.constraint = MatroidConstraint(budget, D, costs)
        self.r = self.constraint.r

    def meet(self, worker):
        weight = Gamma(self.R, self.A + [worker]) - self.U
        if self.constraint.satisfy(self.S + [worker]):
            self.S.append(worker)
            self.A.append(worker)
            self.W[worker] = weight
            self.U += weight
            return worker, None
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
                    return worker, w_
        return None, worker

    def refresh(self, S):
        self.S = S
        self.A = []
        self.W = {}


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
                v = (Gamma(self.R, S + [e]) - Gamma(self.R, S)) / self.constraint.costs[e]
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
    def __init__(self, ID, budget, R, Q):
        self.id = ID
        self.choice_func = None
        self.select_func = None
        self.costs = None
        self.budget = budget
        self.S = []
        self.R = R
        self.Q = Q

    def set_costs(self, costs, D):
        self.costs = costs
        self.choice_func = MChoice(self.S, self.R, self.budget, D, costs)
        self.select_func = BSelect(self.S, self.R, self.budget, costs)

    def choice(self, worker):
        accept, reject = self.choice_func.meet(worker)
        if accept is not None:
            accept.chosen_by(self)
        if reject is not None:
            reject.rejected_by(self)

    def select(self, workers: List):
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
        self.choice_func.refresh(self.S)
        self.select_func.refresh(self.S)

    def prefer(self, new):
        S = self.S
        costs = self.costs
        cost = sum([costs[i] for i in new])
        for i in range(len(S)):
            flag = False
            for R in itertools.combinations(S, i+1):
                A = list(set(S)-set(R))
                if sum([costs[e] for e in A]) + cost <= self.budget:
                    flag = True
                    if Gamma(self.R, A + new) > Gamma(self.R, S):
                        return True
            if not flag:
                return False
        return False


class Worker(Student):
    def __init__(self, ID):
        self.task = None
        self.preference = None
        self.propose_list = None
        self.id = ID

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


def outward_satisfactory(tasks, workers):
    total_matched_pairs = 0
    for task in tasks:
        total_matched_pairs += len(task.students())
    outward_unsatisfied_pairs = 0
    for task in tasks:
        for worker in workers:
            if worker.prefer(task) and task.prefer([task]):
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
        for i in range(len(P)):
            for new in itertools.combinations(P, i+1):
                if task.prefer(new):
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
        sum_utility += q(task.R, task.Q, task.students())
    return sum_utility / len(tasks)
