import itertools

from ccta.Task import Task
from utils.funcs import max_k


def outward_satisfactory(tasks: list[Task], workers, ise=False):
    total_matched_pairs = 0
    for task in tasks:
        total_matched_pairs += len(task.students())
    outward_unsatisfied_pairs = 0
    for task in tasks:
        for worker in workers:
            if worker.prefer(task) and task.prefer([worker], ise):
                outward_unsatisfied_pairs += 1
    return 1 - outward_unsatisfied_pairs / total_matched_pairs


def overall_satisfactory(tasks, workers, ise=False):
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
                if task.prefer(list(new), ise):
                    for worker in new:
                        if not visited[worker]:
                            overall_unsatisfied_pairs += 1
                            visited[worker] = True
    return 1 - overall_unsatisfied_pairs / total_matched_pairs


def waste_pairwise(tasks, workers):
    wasted_pairs = 0
    total_matched_pairs = 0
    for task in tasks:
        total_matched_pairs += len(task.students())
    for task in tasks:
        for worker in workers:
            if worker.prefer(task) and task.have_vacancy_for([worker]):
                wasted_pairs += 1
    return wasted_pairs / total_matched_pairs
