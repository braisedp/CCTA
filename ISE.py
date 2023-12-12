import random
import multiprocessing as mp


class Worker(mp.Process):
    def __init__(self, graph, seeds, outQ, count):
        super(Worker, self).__init__(target=self.start)
        self.graph = graph
        self.seeds = seeds
        self.outQ = outQ
        self.count = count
        self.sum = 0

    def run(self):
        while self.count > 0:
            res = ise(self.graph, self.seeds)
            self.sum += res
            self.count -= 1
            if self.count == 0:
                self.outQ.put(self.sum)


def create_worker(graph, seeds, num, task_num):
    worker = []
    for i in range(num):
        worker.append(Worker(graph, seeds, mp.Queue(), task_num))
        worker[i].start()
    return worker


def finish_worker(worker):
    """
    关闭所有子进程
    :return:
    """
    for w in worker:
        w.terminate()


def ise(graph, seeds):
    return IC(graph, seeds)


def IC(graph, seeds):
    """
    implement independent cascade model
    """
    count = len(seeds)
    activity_set = set(seeds)
    active_nodes = set(seeds)
    while activity_set:
        new_activity_set = set()
        for seed in activity_set:
            for node in graph.neighbors(seed):
                weight = graph[seed][node]['weight']
                if node not in active_nodes:
                    if random.random() < weight:
                        active_nodes.add(node)
                        new_activity_set.add(node)
        count += len(new_activity_set)
        activity_set = new_activity_set
    return count


def calculate_influence(Sk, graph):
    seeds = Sk
    worker_num = 8
    worker = create_worker(graph, seeds, worker_num, int(10000 / worker_num))
    result = []
    for w in worker:
        result.append(w.outQ.get())
    finish_worker(worker)
    return sum(result) / 10000
