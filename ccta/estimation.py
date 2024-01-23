import itertools

from tqdm import tqdm

from ccta.Task import Task
from ccta.Worker import Worker
from utils.funcs import max_k


def fairness_pairwise(tasks: list[Task], workers: list[Worker], ise=False):
    outward_unsatisfied_pairs = 0
    with tqdm(total=len(tasks)*len(workers), desc='estimate fairness-pairwise', leave=True, ncols=100, unit='B',
              unit_scale=True) as pbr:
        for task in tasks:
            for worker in workers:
                if worker.prefer(task) and task.prefer([worker], ise):
                    outward_unsatisfied_pairs += 1
                pbr.update(1)
    qualified_pairs = 0
    for task in tasks:
        for worker in workers:
            if task in worker.preference_list() and task.costs[worker] <= task.budget:
                qualified_pairs += 1
    return 1 - outward_unsatisfied_pairs / qualified_pairs


def overall_satisfactory(tasks: list[Task], workers: list[Worker], ise=False):
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
                if task.have_vacancy_for(list(new)) or task.prefer(list(new), ise):
                    for worker in new:
                        if not visited[worker]:
                            overall_unsatisfied_pairs += 1
                            visited[worker] = True
    qualified_pairs = 0
    for task in tasks:
        for worker in workers:
            if task in worker.preference_list() and task.costs[worker] <= task.budget:
                qualified_pairs += 1
    return 1 - overall_unsatisfied_pairs / qualified_pairs


def waste_pairwise(tasks, workers):
    wasted_pairs = 0
    for task in tasks:
        for worker in workers:
            if worker.prefer(task) and task.have_vacancy_for([worker]):
                wasted_pairs += 1
    qualified_pairs = 0
    for task in tasks:
        for worker in workers:
            if task in worker.preference_list() and task.costs[worker] <= task.budget:
                qualified_pairs += 1
    return wasted_pairs / qualified_pairs




