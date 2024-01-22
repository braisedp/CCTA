from ccta.Task import individual_rationality_tasks, calculate_influence_workers
from ccta.estimation import fairness_pairwise, waste_pairwise
import math
import random
import time
from graph.graph import read_graph_from_csv


def estimate(Tasks, Workers, ise=True):
    if ise:
        for task_ in Tasks:
            task_.estimate()
    result_dict = {'fairness-pairwise': fairness_pairwise(Tasks, Workers, ise),
                   # 'overall_satisfactory': overall_satisfactory(tasks,workers,ise),
                   'individual-rationality': individual_rationality_tasks(Tasks),
                   'waste-pairwise': waste_pairwise(Tasks, Workers)}
    Sum = 0
    Max = 0
    Min = 1000000
    for t_ in Tasks:
        if len(t_.students()) <= 0:
            break
        q = calculate_influence_workers(t_.students(), t_.G, t_.values)/t_.budget
        Sum += q
        if q > Max:
            Max = q
        if q < Min:
            Min = q
    result_dict['average-density'] = Sum/len(Tasks)
    result_dict['maximum-density'] = Max
    result_dict['minimum-density'] = Min
    return result_dict


graph_file = '../graphs/dash/dash.csv'
m = 10  # number of tasks
n = 100  # number of candidate workers
avg_budget = 10
min_cost = 0.05*avg_budget
max_cost = 0.95*avg_budget
Round = 10

if __name__ == '__main__':
    for ii in range(Round):
        graph_file = '../graphs/dash/dash.csv'
        from ccta.Worker import Worker

        g = read_graph_from_csv(graph_file, 0)
        workers = []
        worker_ids = random.sample(list(g.nodes.keys()), n)
        for i in range(n):
            workers.append(Worker(idx=worker_ids[i]))
        del g
        from graph.QIM import sampling
        from utils.funcs import max_k

        # allocate budget to every task, sum of all budget is total_budget
        max_variance = math.ceil(avg_budget / 2)

        budgets = [random.randint(avg_budget - max_variance, avg_budget + max_variance) for _ in range(m)]
        costs = {}
        values = {}
        Q = [0] * m
        g = read_graph_from_csv(graph_file, 0)
        for i in range(m):
            X = [random.uniform(min_cost, max_cost) for _ in range(n)]
            costs[i] = {}
            for j in range(n):
                costs[i][workers[j]] = X[j]

            # values of all workers
            values[i] = {}

            for v in g.nodes:
                values[i][v] = random.uniform(0.0, 1.0)
                Q[i] += values[i][v]
        del g

        from ccta.Task import Task
        from tqdm import tqdm

        tasks = []
        graph_ids = random.sample(range(100), m)
        with tqdm(total=m * 100, desc='generate tasks', leave=True, ncols=100, unit='B', unit_scale=True) as pbar:
            for i in range(m):
                start = time.time()
                G = read_graph_from_csv(graph_file, graph_ids[i])
                budget = budgets[i]
                # generate hyper graph of reverse reachable set in graph G
                k = max_k(budget, costs[i])
                RR = sampling(graph=G, C=worker_ids, k=k, delta=1 / math.pow(n, 2), epsilon=0.001, values=values[i],
                              method='sq')
                pbar.set_postfix({'task': i, 'time used': time.time() - start, 'RR size': len(RR)})

                # initialize tasks
                tasks.append(Task(idx=i, budget=budget, R=RR, Q=Q[i]))
                tasks[i].initialize(costs[i])
                tasks[i].set_graph(G, values[i])
                pbar.update(100)

        for worker in workers:
            value_dict = {}
            for t in tasks:
                value_dict[t] = random.random()
            worker.set_preference(value_dict)

        from stableMatching.Algo import generalized_da

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
            task.set_choice_max_cover()
        generalized_da(tasks, workers)
        estimate(tasks, workers)

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
            task.set_choice_budget()
        generalized_da(tasks, workers)
        estimate(tasks, workers)

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
            task.set_choice_matroid(avg_budget)
        generalized_da(tasks, workers)
        estimate(tasks, workers)

        with tqdm(total=m * 100, desc='generate tasks', leave=True, ncols=100, unit='B', unit_scale=True) as pbar:
            for i in range(m):
                start = time.time()
                # generate hyper graph of reverse reachable set in graph G
                k = max_k(tasks[i].budget, costs[i])
                RR = sampling(graph=tasks[i].G, C=worker_ids, k=k, delta=1 / n, epsilon=0.1, values=values[i],
                              method='normal')
                tasks[i].R = RR
                pbar.set_postfix({'task': i, 'time used': time.time() - start, 'len RR': len(RR)})
                pbar.update(100)

        from stableMatching.Algo import heuristic

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
        heuristic(tasks, workers, 100)
        estimate(tasks, workers)
