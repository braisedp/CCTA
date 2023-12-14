from typing import List

from stable_matching.stableMatching import School, Student


def q(R, Q, workers):
    theta = len(R)
    count = 0
    for rr in R:
        I = 0
        for w in workers:
            if w.idx in rr:
                I = 1
                break
        count += I
    return Q * count / theta


class Task(School):

    def __init__(self, budget: float, R, Q):
        self.workers = []
        self.costs = {}
        self.budget = budget
        self.R = R
        self.Q = Q

    def choice(self, worker):
        pass

    def select(self, workers: List):
        pass

    def preview(self, workers: List):
        pass

    def students(self) -> List:
        pass


class Worker(Student):
    def preview(self, schools: List):
        pass

    def preference_list(self):
        pass

    def propose(self) -> School:
        pass

    def rejected_by(self, school: School):
        pass

    def chosen_by(self, school: School):
        pass

    def school(self) -> School:
        pass

    def matched(self) -> bool:
        pass

    def prefer(self, school) -> bool:
        pass
