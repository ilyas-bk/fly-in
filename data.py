from parser import FileParser


class Data:
    def __init__(self, network: dict):
        self.nb_drones = network['nb_drones']

    def update(self, network: dict) -> dict:
        metadata = network
        # initilization
        first_key = next(iter(metadata['nodes']))
        for node in metadata['nodes']:
            metadata['nodes'][node]['nb_drones'] = 0
        metadata['nodes'][first_key]['nb_drones'] = self.nb_drones
        # drone
        return metadata


class Drone:
    _id_counter = 1
    def __init__(self, start):
        self.id = Drone._id_counter
        Drone._id_counter += 1
        self.position = start


class Node:
    def __init__(self, hub):
        self.__dict__.update(hub)
        self.nb_drones = 0


class Connection:
    def __init__(self, start, end, capacity):
        self.start = start
        self.end = end
        self.capacity = capacity
        self.nb_drones = 0

def main():
    nb_drones = 15
    drone_list = []
    for i in range(nb_drones):
        drone_list.append(Drone("start"))
    for drone in drone_list:
        print(f"Updating drone D{drone.id}...")

if __name__ == "__main__":
    import json
    main()

    # parser = FileParser("03_ultimate_challenge.txt")
    # try:
    #     parser.read_file()
    #     result = parser.parse()
    #     data = Data(result)
    #     result = data.update(result)
    #     print(json.dumps(result, indent=2))
    # except (ValueError, FileNotFoundError) as e:
    #     print(e)
