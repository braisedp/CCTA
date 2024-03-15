import pandas as pd

from ccta.Task import individual_rationality_tasks, calculate_influence_workers
from ccta.estimation import fairness_pairwise, waste_pairwise
import math
import random
import time
from graph.graph import read_graph_from_csv


def estimate(Tasks, Workers, ise=False):
    if ise:
        for task_ in Tasks:
            task_.estimate()
    result_dict = {'fairness-pairwise': fairness_pairwise(Tasks, Workers, ise),
                   # 'overall_satisfactory': overall_satisfactory(tasks,workers,ise),
                   # 'individual-rationality': individual_rationality_tasks(Tasks),
                   'waste-pairwise': waste_pairwise(Tasks, Workers)}
    Sum = 0
    Max = 0
    Min = 1000000
    for t_ in Tasks:
        if len(t_.students()) <= 0:
            break
        q = calculate_influence_workers(t_.students(), t_.G, t_.values) / t_.budget
        Sum += q
        if q > Max:
            Max = q
        if q < Min:
            Min = q
    result_dict['avg-density'] = Sum / len(Tasks)
    result_dict['max-density'] = Max
    result_dict['min-density'] = Min
    return result_dict


graph_name = 'dash'
graph_file = '../graphs/{}/{}.csv'.format(graph_name, graph_name)
result_file = './result/{}.csv'.format(graph_name)
m = 10  # number of tasks
n = 600  # number of candidate workers
avg_budget = 1.0
epsilon = 0.05
min_cost = epsilon
max_cost = (1 - epsilon)
epochs = range(5)

if __name__ == '__main__':
    for epoch in epochs:
        graph_file = '../graphs/dash/dash.csv'
        from ccta.Worker import Worker

        g = read_graph_from_csv(graph_file, 0)
        workers = []
        worker_ids = random.sample(list(g.nodes.keys()), n)
        for i in range(n):
            workers.append(Worker(idx=worker_ids[i]))
        del g
        from graph.QIM import sampling, generate_estimation
        from utils.funcs import max_k

        # allocate budget to every task, sum of all budget is total_budget
        max_variance = avg_budget / 2

        budgets = [random.uniform(avg_budget - max_variance, avg_budget + max_variance) for _ in range(m)]
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
        with tqdm(total=m * 100, desc='generate tasks', leave=True, ncols=150, unit='B', unit_scale=True) as pbar:
            pbar.set_description('round:{},generate tasks'.format(epoch))
            for i in range(m):
                start = time.time()
                G = read_graph_from_csv(graph_file, graph_ids[i])
                budget = budgets[i]
                # generate hyper graph of reverse reachable set in graph G
                k = max_k(budget, costs[i])
                RR = sampling(graph=G, C=worker_ids, k=k, delta=1/n, epsilon=0.01, values=values[i],
                              method='modified')
                pbar.set_postfix({'task': i, 'time used': time.time() - start, 'RR size': len(RR)})

                # initialize tasks
                tasks.append(Task(idx=i, budget=budget, R=RR, Q=Q[i]))
                tasks[i].initialize(costs[i])
                tasks[i].set_graph(G, values[i])
                pbar.update(100)

        with tqdm(total=m * 100, desc='generate estimation', leave=True, ncols=150, unit='B', unit_scale=True) as pbar:
            pbar.set_description('round:{},generate estimation'.format(epoch))
            for i in range(m):
                RR = generate_estimation(graph=tasks[i].G, values=values[i], count=100000)
                tasks[i].set_estimation_rr(RR)
                pbar.set_postfix({'task': i})
                pbar.update(100)

        for worker in workers:
            value_dict = {}
            for t in tasks:
                value_dict[t] = random.random()
            worker.set_preference(value_dict)

        result = {}

        from stableMatching.Algo import generalized_da

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
            task.set_choice_max_cover()
        generalized_da(tasks, workers)
        result['max-cover'] = estimate(tasks, workers)

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
            task.set_choice_budget()
        generalized_da(tasks, workers)
        result['budget'] = estimate(tasks, workers)

        # for worker in workers:
        #     worker.refresh()
        # for task in tasks:
        #     task.refresh()
        #     task.set_choice_matroid(math.ceil(10*avg_budget))
        # generalized_da(tasks, workers)
        # result['matroid'] = estimate(tasks, workers)

        with tqdm(total=m * 100, leave=True, ncols=150, unit='B', unit_scale=True) as pbar:
            pbar.set_description('round:{},regenerate RR'.format(epoch))
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
        heuristic(tasks, workers, 5)
        result['heuristic'] = estimate(tasks, workers)

        df = pd.read_csv(result_file).reset_index(drop=True)
        methods = ['max-cover', 'budget', 'heuristic']
        # methods = ['matroid']
        for method in methods:
            s = pd.Series([epoch, method, m, n, avg_budget, result[method]['fairness-pairwise'],
                           result[method]['waste-pairwise'], result[method]['avg-density'],
                           result[method]['max-density'], result[method]['min-density']],
                          index=['round', 'method', 'task', 'worker', 'avg-budget', 'fairness-pairwise',
                                 'waste-pairwise', 'avg-density', 'max-density', 'min-density'])
            df.loc[len(df)] = s
        df.reset_index(drop=True)
        df.to_csv(result_file, index=False)

        del tasks, workers, df
