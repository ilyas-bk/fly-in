from parser import FileParser
from data import Data, Drone
from simulation import Simulation


class Flyin:
    pass


def produce_drones(nb_drones):
    drone_list = []
    for _ in range(nb_drones):
        drone_list.append(Drone("start"))
    return drone_list


def parse():
    parser = FileParser("02_capacity_hell.txt")
    try:
        parser.read_file()
        network = parser.parse()
        metadata = Data(network)
        network = metadata.update(network)
    except (ValueError, FileNotFoundError) as e:
        print(e)
    return network


if __name__ == "__main__":
    network = parse()
    drones = produce_drones(12)
    simulation = Simulation()
    simulation.run(network['nodes'], drones)
