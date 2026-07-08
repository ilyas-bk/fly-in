from parser import FileParser
from display import Display
from data import Data

if __name__ == "__main__":
    parser = FileParser("02_capacity_hell.txt")
    try:
        parser.read_file()
        network = parser.parse()
        metadata = Data(network)
        network = metadata.update(network)
    except (ValueError, FileNotFoundError) as e:
        print(e)
    display = Display()
    display.display(network['nodes'])
