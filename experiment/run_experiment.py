import math

import pandas as pd

from ccta.Task import individual_rationality_tasks, calculate_influence_workers, gamma_workers
from ccta.Worker import Worker
from ccta.estimation import fairness_pairwise, waste_pairwise, overall_satisfactory
import random
import time
from graph.graph import read_graph, read_graphs


def estimate(Tasks, Workers):
    result_dict = {
        'fairness-pairwise': fairness_pairwise(Tasks, Workers),
        # 'overall-satisfactory': overall_satisfactory(Tasks, Workers),
        # 'individual-rationality': individual_rationality_tasks(Tasks),
        # 'waste-pairwise': waste_pairwise(Tasks, Workers)
    }
    Sum = 0
    for t_ in Tasks:
        if len(t_.students()) <= 0:
            continue
        q = gamma_workers(t_.es_RR, t_.students()) * t_.Q / len(t_.es_RR)
        Sum += q
    result_dict['avg-quality'] = Sum / len(Tasks)

    Sum2 = 0
    for w_ in Workers:
        q = 0
        if w_.task is not None:
            q = 1-w_.preference_list().index(w_.task)/len(w_.preference_list())
        Sum2 += q
    result_dict['avg-utility'] = Sum2/len(Workers)
    return result_dict


graph_name = 'dash'
graph_file = '../graphs/{}.csv'.format(graph_name)
result_file = './result/{}_result.csv'.format(graph_name)
m = 160  # number of tasks
n = 600  # number of candidate workers
avg_budget = 1.0
min_cost = 0.1
max_cost = 0.5
epochs = range(5)

if __name__ == '__main__':
    for epoch in epochs:

        g = read_graph(graph_file, wcol=0, sep=',', directed=True)
        size = g.vcount()
        del g
        workers = []
        worker_ids = random.sample(range(size), n)
        for i in range(n):
            workers.append(Worker(idx=worker_ids[i]))
        from graph.QIM import sampling, generate_estimation
        from utils.funcs import max_k

        # allocate budget to every task, sum of all budget is total_budget

        budgets = [avg_budget for _ in range(m)]
        costs = {}
        values = {}
        Q = [0] * m
        for i in range(m):
            X = [random.uniform(min_cost, max_cost) for _ in range(n)]
            costs[i] = {}
            for j in range(n):
                costs[i][workers[j]] = X[j]

            # values of all workers
            values[i] = {}

            for v in range(size):
                values[i][v] = random.uniform(0.0, 1.0)
                Q[i] += values[i][v]

        from ccta.Task import Task
        from tqdm import tqdm

        tasks = []
        graph_ids = random.sample(range(500), m)
        graphs = read_graphs(graph_file, cols=graph_ids, sep=',', directed=True)
        with tqdm(total=m * 100, desc='generate tasks', leave=True, ncols=150, unit='B', unit_scale=True) as pbar:
            pbar.set_description('round:{},generate tasks'.format(epoch))
            for i in range(m):
                start = time.time()
                G = graphs[i]
                budget = budgets[i]
                # generate hyper graph of reverse reachable set in graph G
                k = max_k(budget, costs[i])
                RR = sampling(graph=G, C=worker_ids, k=k, delta=1 / math.pow(m, 2), epsilon=0.01, values=values[i],
                              method='normal')
                # RR = generate_estimation(graph=G, values=values[i], count=2000)
                pbar.set_postfix({'task': i, 'time used': time.time() - start, 'RR size': len(RR)})

                # initialize tasks
                tasks.append(Task(idx=i, budget=budget, R=RR, Q=Q[i]))
                tasks[i].initialize(costs[i])
                pbar.update(100)

        for worker in workers:
            value_dict = {}
            for t in tasks:
                value_dict[t] = random.random()
            worker.set_preference(value_dict)

        result = {}

        with tqdm(total=m * 100, desc='generate estimation', leave=True, ncols=150, unit='B', unit_scale=True) as pbar:
            pbar.set_description('round:{},generate estimation'.format(epoch))
            for i in range(m):
                RR = generate_estimation(graph=graphs[i], values=values[i], count=100000)
                tasks[i].set_estimation_rr(RR)
                pbar.set_postfix({'task': i})
                pbar.update(100)

        del graphs

        from stableMatching.Algo import generalized_da

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
            task.set_choice_budget()
        generalized_da(tasks, workers)
        result['budget'] = estimate(tasks, workers)

        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
            task.set_choice_max_cover()
        generalized_da(tasks, workers)
        result['max-cover'] = estimate(tasks, workers)

        # with tqdm(total=m * 100, leave=True, ncols=150, unit='B', unit_scale=True) as pbar:
        #     pbar.set_description('round:{},regenerate RR'.format(epoch))
        #     for i in range(m):
        #         start = time.time()
        #         # generate hyper graph of reverse reachable set in graph G
        #         k = max_k(tasks[i].budget, costs[i])
        #         RR = sampling(graph=tasks[i].G, C=worker_ids, k=k, delta=1 / math.pow(m, 2), epsilon=0.001,
        #         values=values[i], method='normal')
        #         tasks[i].R = RR
        #         pbar.set_postfix({'task': i, 'time used': time.time() - start, 'len RR': len(RR)})
        #         pbar.update(100)

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
            s = pd.Series([epoch, method, m, n, result[method]['fairness-pairwise'], result[method]['avg-quality'],
                           result[method]['avg-utility']],
                          index=['round', 'method', 'task', 'worker', 'fairness-pairwise', 'avg-quality', 'avg-utility'])
            df.loc[len(df)] = s
        df.reset_index(drop=True)
        df.to_csv(result_file, index=False)

        del tasks, workers, df, result, costs, values, Q, budgets
