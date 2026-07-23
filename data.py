from parser import FileParser

# need to make a method to get the change the position of a drone -> logic.py
class Network:
    def __init__(self, network: dict):
        self.network = network
        self.nb_drones = network['nb_drones']

    def update(self, network: dict) -> dict:
        metadata = network
        first_zone = next(iter(metadata['zones']))
        last_zone = next(reversed(metadata['zones']))
        metadata['zones'][first_zone]['max_drones'] = self.nb_drones
        metadata['zones'][last_zone]['max_drones'] = self.nb_drones
        return metadata

    @staticmethod
    def parse(file) -> dict:
        parser = FileParser(file)
        network = dict()
        try:
            parser.read_file()
            network = parser.parse()
            metadata = Network(network)
            network = metadata.update(network)
        except (ValueError, FileNotFoundError) as e:
            print(e)
        return network


class Drone:
    _id_counter = 1
    def __init__(self, start):
        self.id = Drone._id_counter
        Drone._id_counter += 1
        self.path_idx = 0
        self.position = start
        self.path = []
        self.wait = 0

    def update(self):
        pass

    @staticmethod
    def init_drones(nb_drones: int) -> list:
        drone_list = []
        for _ in range(nb_drones):
            drone_list.append(Drone("start"))
        return drone_list

# must transform the parsed data to instances from this class
class Zone:
    def __init__(self, zone, name):
        self.__dict__.update(zone)
        self.name = name
        self.curr_drones = zone['current_drones']
        self.capacity = zone['max_drones']
        self.neighbors = zone['neighbors']
        self.connections = zone['connections']
        self.type = zone['zone_type']

    def update(self):
        pass

    @staticmethod
    def init_zones(network: dict) -> list:
        zones = []
        for key, value in network['zones'].items():
            zones.append(Zone(value, key))
        return zones


if __name__ == "__main__":
    import json
    network = Network.parse("02_capacity_hell.txt")
    zones = Zone.init_zones(network)
    drones = Drone.init_drones(network['nb_drones'])
    print(json.dumps(network, indent=2))
