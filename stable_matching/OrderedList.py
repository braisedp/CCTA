class OrderedList:
    def __init__(self):
        self.items = []
        self.values = []
        self.save_frac = 1.0

    def insert(self, item, value):
        i = 0
        while i < len(self.items):
            if self.values[i] > value:
                break
            i += 1
        self.items.insert(i, item)
        self.values.insert(i, value)

    def get(self, i):
        return self.items[i]

    def remove(self, item):
        i = self.items.index(item)
        self.items.remove(i)
        self.values.pop(i)