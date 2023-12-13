import random
from typing import List

from stableMatching import School, Student, generalized_da


class Hospital(School):

    def __init__(self, i, capacity: int):
        self.i = i
        self.preference = {}
        self.doctors = []
        self.capacity = capacity

    def choice(self, doctor):
        if len(self.doctors) >= self.capacity:
            d = max(self.doctors, key=lambda x: self.preference[x])
            idx = self.preference[doctor]
            if idx < self.preference[d]:
                self.doctors.remove(d)
                self.doctors.append(doctor)
                d.rejected_by(self)
                doctor.chosen_by(self)
            else:
                doctor.rejected_by(self)
        else:
            self.doctors.append(doctor)
            doctor.chosen_by(self)

    def select(self, doctors: List) -> List:
        sorted(doctors, key=lambda x: self.preference[x])
        while len(doctors) > self.capacity:
            doctors.pop()
        return doctors

    def preview(self, students: List):
        n = len(students)
        p = random.sample([i for i in range(n)], n)
        for i in range(n):
            self.preference[students[i]] = p[i]

    def students(self) -> List:
        return self.doctors


class Doctor(Student):
    def __init__(self, i):
        self.i = i
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


def test():
    hospitals = [Hospital(i, 2) for i in range(3)]
    doctors = [Doctor(i) for i in range(8)]
    hospitals, doctors = generalized_da(hospitals, doctors)
    for hospital in hospitals:
        p = sorted(hospital.preference.keys(), key=lambda x: hospital.preference[x])
        print('hospital:{},preference:{}'.format(hospital.i, [d.i for d in p]))
    for doctor in doctors:
        p = sorted(doctor.preference.keys(), key=lambda x: doctor.preference[x])
        print('doctor:{},preference:{}'.format(doctor.i, [h.i for h in p]))

    for hospital in hospitals:
        print('hospital:{},doctors:{}'.format(hospital.i, [d.i for d in hospital.doctors]))


if __name__ == "__main__":
    test()
