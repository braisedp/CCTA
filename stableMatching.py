from abc import ABCMeta, abstractmethod
from typing import List


class Hospital(metaclass=ABCMeta):
    @abstractmethod
    def choice(self, students: List) -> List:
        pass

    @abstractmethod
    def capable(self, students: List) -> List:
        pass

    @abstractmethod
    def get_students(self) -> List:
        pass

    @abstractmethod
    def set_students(self, students: List):
        pass

    @abstractmethod
    def matched(self) -> bool:
        pass


class Student(metaclass=ABCMeta):
    @abstractmethod
    def choice(self, hospitals: List) -> List:
        pass

    @abstractmethod
    def capable(self, hospitals: List) -> List:
        pass

    @abstractmethod
    def hospital(self) -> Hospital:
        pass

    @abstractmethod
    def get_hospital(self) -> List:
        pass

    @abstractmethod
    def set_hospital(self, students: List):
        pass

    @abstractmethod
    def matched(self) -> bool:
        pass

def matched(students:List) -> bool:
    flag = True
    for s in students:
        if not s.matched:
            flag = False
    return flag

def choose(students:List) -> Student:
    l = filter(lambda s:not s.matched, students)

def generalized_da(hospitals: List, students: List):
    dict_h = {}
    for h in hospitals:
        dict_h.update({h, h.capable(students)})

    dict_s = {}
    for s in students:
        dict_s.update({s, s.capable(hospitals)})

    while not matched(students):

