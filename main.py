from src import Simulation, SolutionLogic, Network

if __name__ == "__main__":
    try:
        network = Network.parse("map.txt")
        solution = SolutionLogic(network)
        simulation = Simulation()
        simulation.run(solution)
    except KeyboardInterrupt:
        print("\nkeyboard interrupted")
