import random
from typing import List


class School:
    def choice(self, student):
        pass

    def select(self, students: List):
        pass

    def preview(self, students: List):
        pass

    def students(self) -> List:
        pass


class Student:

    def preview(self, schools: List):
        pass

    def preference_list(self):
        pass

    def propose(self) -> School:
        pass

    def rejected_by(self, school):
        pass

    def chosen_by(self, school):
        pass

    def school(self):
        pass

    def matched(self) -> bool:
        pass

    def prefer(self, school) -> bool:
        pass


def all_matched(students: List) -> bool:
    for s in students:
        if not s.matched():
            return False
    return True


def find(students: List) -> Student:
    student_list = list(filter(lambda s: not s.matched(), students))
    return random.choice(student_list)


def generalized_da(schools: List, students: List):
    for student in students:
        student.preview(schools)
    for school in schools:
        school.preview(students)
    while not all_matched(students):
        student = find(students)
        school = student.propose()
        school.choice(student)


def heuristic(schools: List, students: List, k: int):
    for student in students:
        student.preview(schools)
    for school in schools:
        school.preview(students)
    for i in range(k):
        for school in schools:
            student_list = school.students().copy()
            for student in students:
                if school in student.preference_list() and student.prefer(school):
                    student_list.append(student)
            school.select(student_list)
