from src import Simulation, SolutionLogic, Network
import sys

if __name__ == "__main__":
    try:
        network = Network.parse(sys.argv[1])
        solution = SolutionLogic(network)
        simulation = Simulation()
        simulation.run(solution)
    except KeyboardInterrupt:
        print("\nkeyboard interrupted")
    except IndexError:
        print("Usage: python main.py <map_file>")
    except Exception as e:
        print(f"An error occurred: {e}")
