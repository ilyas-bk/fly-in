
class Drone:
    _id_counter = 1
    def __init__(self):
        self.id = "D" + str(Drone._id_counter)
        Drone._id_counter += 1
        self.position: list


class Hub:
    def __init__(self, hub):
        self.__dict__.update(hub)


class Connection:
    def __init__(self, start, end, capacity):
        self.start = start
        self.end = end
        self.capacity = capacity
