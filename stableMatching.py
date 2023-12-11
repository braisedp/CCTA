import random
from abc import ABCMeta, abstractmethod
from typing import List


class Hospital(metaclass=ABCMeta):
    @abstractmethod
    def choice(self, students: List) -> List:
        pass

    @abstractmethod
    def select(self, students: List) -> List:
        pass

    @abstractmethod
    def capable(self, students: List) -> List:
        pass

    @abstractmethod
    def students(self) -> List:
        pass

    @abstractmethod
    def matched(self) -> bool:
        pass


class Student(metaclass=ABCMeta):

    @abstractmethod
    def init_preference_list(self, hospitals: List):
        pass

    @abstractmethod
    def preference_list(self):
        pass

    @abstractmethod
    def propose(self) -> Hospital:
        pass

    @abstractmethod
    def rejected_by(self, hospital: Hospital):
        pass

    @abstractmethod
    def hospital(self) -> Hospital:
        pass

    @abstractmethod
    def matched(self) -> bool:
        pass

    @abstractmethod
    def prefer(self, hospital1, hospital2) -> bool:
        pass


def all_matched(students: List) -> bool:
    flag = True
    for s in students:
        if not s.matched:
            flag = False
    return flag


def choose(students: List) -> Student:
    l = filter(lambda s: not s.matched, students)
    return random.choice(l)


def generalized_da(hospitals: List, students: List):
    for student in students:
        student.init_preference_list(hospitals)
    while not all_matched(students):
        student = choose(students)
        h = student.propose()
        h.choice(h.students() + [student])
    return hospitals, students


def heuristic(hospitals: List, students: List, k: int):
    for i in range(k):
        for hospital in hospitals:
            s_h = hospital.students().copy()
            for student in students:
                if hospital in student.preference_list() and student.prefer(hospital, student.hospital()):
                    s_h.append(student)
            hospital.select(s_h)
