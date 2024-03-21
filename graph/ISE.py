import random
import multiprocessing as mp


class Worker(mp.Process):
    def __init__(self, graph, seeds, values, outQ, count):
        super(Worker, self).__init__(target=self.start)
        self.graph = graph
        self.seeds = seeds
        self.values = values
        self.outQ = outQ
        self.count = count
        self.sum = 0

    def run(self):
        while self.count > 0:
            res = ise(self.graph, self.seeds, self.values)
            self.sum += res
            self.count -= 1
            if self.count == 0:
                self.outQ.put(self.sum)


def create_worker(graph, seeds, values, num, task_num):
    worker = []
    for i in range(num):
        worker.append(Worker(graph, seeds, values, mp.Queue(), task_num))
        worker[i].start()
    return worker


def finish_worker(worker):
    """
    关闭所有子进程
    :return:
    """
    for w in worker:
        w.terminate()


def ise(graph, seeds, values):
    return IC_v(graph, seeds, values)


def IC_v(graph, seeds, values):
    count = sum([values[seed] for seed in seeds])
    activity_set = set(seeds)
    active_nodes = set(seeds)
    while activity_set:
        new_activity_set = set()
        for seed in activity_set:
            for node in graph.neighbors(seed):
                weight = graph.es[graph.get_eid(seed, node)]['weight']
                if node not in active_nodes:
                    if random.random() < weight:
                        active_nodes.add(node)
                        count += values[node]
                        new_activity_set.add(node)
        activity_set = new_activity_set
    return count


def calculate_influence_quality(Sk, graph, values, times=500, multi=False):
    seeds = Sk
    worker_num = 4
    result = []
    if multi:
        worker = create_worker(graph, seeds, values, worker_num, int(times / worker_num))
        # print([w.pid for w in worker])
        for w in worker:
            result.append(w.outQ.get())
        finish_worker(worker)
    else:
        for i in range(times):
            result.append(IC_v(graph, seeds, values))
    return sum(result) / times
