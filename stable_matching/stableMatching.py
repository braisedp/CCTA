import random
from abc import ABCMeta, abstractmethod
from typing import List


class School(metaclass=ABCMeta):
    @abstractmethod
    def choice(self, student):
        pass

    @abstractmethod
    def select(self, students: List):
        pass

    @abstractmethod
    def preview(self, students: List):
        pass

    @abstractmethod
    def students(self) -> List:
        pass


class Student(metaclass=ABCMeta):

    @abstractmethod
    def preview(self, schools: List):
        pass

    @abstractmethod
    def preference_list(self):
        pass

    @abstractmethod
    def propose(self) -> School:
        pass

    @abstractmethod
    def rejected_by(self, school: School):
        pass

    @abstractmethod
    def chosen_by(self, school: School):
        pass

    @abstractmethod
    def school(self) -> School:
        pass

    @abstractmethod
    def matched(self) -> bool:
        pass

    @abstractmethod
    def prefer(self, school) -> bool:
        pass


def all_matched(students: List) -> bool:
    flag = True
    for s in students:
        if not s.matched():
            flag = False
    return flag


def choose(students: List) -> Student:
    l = list(filter(lambda s: not s.matched(), students))
    return random.choice(l)


def generalized_da(schools: List, students: List):
    for student in students:
        student.preview(schools)
    for school in schools:
        school.preview(students)
    while not all_matched(students):
        student = choose(students)
        school = student.propose()
        school.choice(student)


def heuristic(schools: List, students: List, k: int):
    for student in students:
        student.preview(schools)
    for school in schools:
        school.preview(students)
    for i in range(k):
        for school in schools:
            l = school.students().copy()
            for student in students:
                if school in student.preference_list() and student.prefer(school):
                    l.append(student)
            school.select(l)
