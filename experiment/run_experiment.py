import math

import pandas as pd

from ccta.Task import individual_rationality_tasks, calculate_influence_workers, gamma_workers, Task
from ccta.Worker import Worker
from ccta.estimation import fairness_pairwise, waste_pairwise, overall_satisfactory
import random
import time
from graph.graph import read_graph, read_graphs


def estimate(Tasks, Workers):
    result_dict = {
        'fairness-pairwise': fairness_pairwise(Tasks, Workers),
        # 'overall-satisfactory': overall_satisfactory(Tasks, Workers),
        'individual-rationality': individual_rationality_tasks(Tasks),
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
            q = 1 - w_.preference_list().index(w_.task) / len(w_.preference_list())
        Sum2 += q
    result_dict['avg-utility'] = Sum2 / len(Workers)
    return result_dict


def run_experiment(graph_file, result_file, m, n, avg_budget, min_cost, max_cost, epochs):
    for epoch in epochs:
        tasks, workers = init_environment(graph_file, m, n, avg_budget, min_cost, max_cost, epoch)
        result = matching(tasks, workers)
        save_results(result, result_file, epoch, m, n)


def init_environment(graph_file, m, n, avg_budget, min_cost, max_cost, epoch) -> tuple[list[Task], list[Worker]]:
    g = read_graph(graph_file, wcol=0, sep=',', directed=True)
    size = g.vcount()
    del g
    workers = []
    worker_ids = random.sample(range(size), n)
    for i in range(n):
        workers.append(Worker(idx=worker_ids[i]))

    from graph.QIM import sampling, generate_estimation
    from utils.funcs import max_k

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

    with tqdm(total=m * 100, desc='generate estimation', leave=True, ncols=150, unit='B', unit_scale=True) as pbar:
        pbar.set_description('round:{},generate estimation'.format(epoch))
        for i in range(m):
            RR = generate_estimation(graph=graphs[i], values=values[i], count=100000)
            tasks[i].set_estimation_rr(RR)
            pbar.set_postfix({'task': i})
            pbar.update(100)

    return tasks, workers


def matching(tasks: list[Task], workers: list[Worker]) -> dict:
    result = {}
    from stableMatching.Algo import generalized_da

    for worker in workers:
        worker.refresh()
    for task in tasks:
        task.refresh()
        task.set_choice_budget()
    turn = generalized_da(tasks, workers)
    result['budget'] = estimate(tasks, workers)
    result['budget']['turn'] = turn

    for worker in workers:
        worker.refresh()
    for task in tasks:
        task.refresh()
        task.set_choice_max_cover()
    generalized_da(tasks, workers)
    result['max-cover'] = estimate(tasks, workers)
    result['max-cover']['turn'] = turn

    from stableMatching.Algo import heuristic

    for worker in workers:
        worker.refresh()
    for task in tasks:
        task.refresh()
    heuristic(tasks, workers, 5)
    result['heuristic'] = estimate(tasks, workers)
    result['heuristic']['turn'] = 0
    return result


def save_results_individual_rational(result, result_file, m, n):
    df = pd.read_csv(result_file).reset_index(drop=True)
    methods = ['max-cover', 'budget', 'heuristic']
    for method in methods:
        for i in range(m):
            s = pd.Series([method, result[method]['individual-rationality'][i][1]], index=['method', 'cost'])
            df.loc[len(df)] = s
    df.reset_index(drop=True)
    df.to_csv(result_file, index=False)


def save_results(result, result_file, epoch, m, n):
    df = pd.read_csv(result_file).reset_index(drop=True)
    methods = ['budget','max-cover','heuristic']
    # methods = ['matroid']
    for method in methods:
        s = pd.Series([epoch, method, m, n,
                       result[method]['fairness-pairwise'],
                       # result[method]['overall-satisfactory'],
                       result[method]['avg-quality'],
                       result[method]['avg-utility'],
                       result[method]['turn']
                       ],
                      index=['round', 'method', 'task', 'worker',
                             'fairness-pairwise',
                             # 'overall-satisfactory',
                             'avg-quality',
                             'avg-utility',
                             'turn'
                             ])
        df.loc[len(df)] = s
        # mask = (df['round'] == epoch) & (df['method'] == method) & (df['task'] == m) & (
        #         df['worker'] == n)
        # df.loc[mask, 'turn'] = result[method]
    df.reset_index(drop=True)
    df.to_csv(result_file, index=False)


def estimate_heuristic(tasks: list[Task], workers: list[Worker], K: int):
    from stableMatching.Algo import heuristic
    result = {}
    for k in range(K):
        for worker in workers:
            worker.refresh()
        for task in tasks:
            task.refresh()
        heuristic(tasks, workers, k)
        result[k] = estimate(tasks, workers)
    return result


def run_estimate_heuristic(graph_file, graph_name, result_file, m, n, K, avg_budget, min_cost, max_cost, epochs):
    for epoch in epochs:
        tasks, workers = init_environment(graph_file, m, n, avg_budget, min_cost, max_cost, epoch)
        result = estimate_heuristic(tasks, workers, K)
        save_result_heuristic(result, result_file, K, graph_name, m, n, epoch)


def run_estimate_individual(graph_file, result_file, m, n, avg_budget, min_cost, max_cost):
    tasks, workers = init_environment(graph_file, m, n, avg_budget, min_cost, max_cost, 0)
    result = matching(tasks, workers)
    save_results_individual_rational(result, result_file, m, n)


def save_result_heuristic(result, result_file, K, graph_name, m, n, epoch):
    df = pd.read_csv(result_file).reset_index(drop=True)
    for k in range(K):
        s = pd.Series([epoch, graph_name, m, n, k,
                       result[k]['fairness-pairwise']],
                      index=['epoch', 'dataset', 'task', 'worker', 'k',
                             'fairness-pairwise'
                             ])
        df.loc[len(df)] = s
    df.reset_index(drop=True)
    df.to_csv(result_file, index=False)


def run_heuristic(graph_name, m_list, n, K):
    graph_file = './graphs/{}.csv'.format(graph_name)
    result_file = './experiment/result/heuristic_result.csv'
    avg_budget = 1.0
    min_cost = 0.1
    max_cost = 0.5
    epochs = range(1)
    for m in m_list:
        run_estimate_heuristic(graph_file, graph_name, result_file, m, n, K, avg_budget, min_cost, max_cost, epochs)


def run(graph_name, m_list, n):
    graph_file = './graphs/{}.csv'.format(graph_name)
    result_file = './experiment/result/{}_result.csv'.format(graph_name)
    avg_budget = 1.0
    min_cost = 0.1
    max_cost = 0.5
    epochs = range(10)
    for m in m_list:
        run_experiment(graph_file, result_file, m, n, avg_budget, min_cost, max_cost, epochs)


def run_individual_rational(graph_name, m_list, n):
    graph_file = './graphs/{}.csv'.format(graph_name)
    result_file = './experiment/result/{}_result_individual.csv'.format(graph_name)
    avg_budget = 1.0
    min_cost = 0.1
    max_cost = 0.5
    for m in m_list:
        run_estimate_individual(graph_file, result_file, m, n, avg_budget, min_cost, max_cost)