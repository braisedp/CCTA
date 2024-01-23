from stableMatching.Student import Student


class Worker(Student):
    def __init__(self, idx: int):
        self.task = None
        self.preference = list()
        self.propose_list = list()
        self.idx = idx

    def refresh(self):
        self.task = None
        self.propose_list = self.preference.copy()

    def set_preference(self, values):
        self.preference = sorted(values.keys(), key=lambda x: values[x], reverse=True)
        self.propose_list = self.preference.copy()

    def preview(self, schools: list):
        pass

    def preference_list(self):
        return self.preference

    def propose(self):
        return self.propose_list[0]

    def rejected_by(self, task):
        self.propose_list.remove(task)
        self.task = None

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
        if task is None or task not in self.preference:
            return False
        if self.task is None:
            return True
        return self.preference.index(task) < self.preference.index(self.task)

    def __str__(self):
        return str(self.idx)
