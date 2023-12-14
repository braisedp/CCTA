import random
from typing import List

from stableMatching import School, Student


class Hospital(School):

    def __init__(self, i, capacity: int):
        self.i = i
        self.doctors = []
        self.capacity = capacity

    def choice(self, doctor):
        if len(self.doctors) >= self.capacity:
            d = max(self.doctors, key=lambda x: x.score)
            if doctor.score > d.score:
                self.doctors.remove(d)
                self.doctors.append(doctor)
                d.rejected_by(self)
                doctor.chosen_by(self)
            else:
                doctor.rejected_by(self)
        else:
            self.doctors.append(doctor)
            doctor.chosen_by(self)

    def select(self, doctors: List):
        sorted(doctors, key=lambda x: x.score)
        while len(doctors) > self.capacity:
            d = doctors.pop()
            if d in self.doctors:
                d.hospital = None
        for d in doctors:
            if d not in self.doctors:
                if d.hospital is not None:
                    d.hospital.doctors.remove(d)
                d.hospital = self
        self.doctors = doctors

    def preview(self, students: List):
        pass

    def students(self) -> List:
        return self.doctors

    def refresh(self):
        self.doctors = []


class Doctor(Student):
    def __init__(self, i, score):
        self.i = i
        self.preference = {}
        self.p_list = []
        self.hospital = None
        self.score = score

    def refresh(self):
        self.preference = {}
        self.p_list = []
        self.hospital = None

    def preview(self, hospitals: List):
        n = len(hospitals)
        p = random.sample([i for i in range(n)], n)
        for i in range(n):
            self.preference[hospitals[i]] = p[i]
        self.p_list = sorted(hospitals, key=lambda x: self.preference[x])

    def preference_list(self):
        return self.preference.keys()

    def propose(self) -> School:
        if len(self.p_list) > 0:
            return self.p_list[0]

    def rejected_by(self, hospital: School):
        self.p_list.remove(hospital)
        self.hospital = None

    def chosen_by(self, hospital: School):
        self.hospital = hospital

    def matched(self) -> bool:
        if self.hospital is not None or len(self.p_list) == 0:
            return True
        return False

    def school(self) -> School:
        return self.hospital

    def prefer(self, hospital) -> bool:
        if hospital is None:
            return False
        if self.hospital is None:
            return True
        return self.preference[hospital] > self.preference[self.hospital]
