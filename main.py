from parser import FileParser
from display import Display

if __name__ == "__main__":
    parser = FileParser("03_ultimate_challenge.txt")
    try:
        parser.read_file()
        network = parser.parse()
    except (ValueError, FileNotFoundError) as e:
        print(e)
    display = Display()
    display.display(network['nodes'])
