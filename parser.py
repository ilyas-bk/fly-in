import re
from typing import Any


# still need to fix the error handling in this class
class FileParser:
    PATTERNS = {
        'nb_drones_patt': re.compile(
            r"^nb_drones:\s+"
            r"(?P<nb_drones>\d+)$"),
        'start_hub_patt': re.compile(
            r"^start_hub:\s+(?P<name>\w+)\s+"
            r"(?P<x>[-]?\d+)\s+(?P<y>[-]?\d+)\s*"
            r"\[(color=(?P<color>\w+)\s*)?"
            r"(max_drones=(?P<max_drones>\w+))?"
            r"\]$"
        ),
        'hub_patt' : re.compile(
            r"^hub:\s+(?P<name>\w+)\s+"
            r"(?P<x>[-]?\d+)\s+(?P<y>[-]?\d+)\s+"
            r"\[(zone=(?P<zone>\w+)\s*)?"
            r"(color=(?P<color>\w+)\s*)?"
            r"(max_drones=(?P<max_drones>\w+))?"
            r"\]$"
        ),
        'end_hub_patt': re.compile(
            r"^end_hub:\s+(?P<name>\w+)\s+"
            r"(?P<x>[-]?\d+)\s+(?P<y>[-]?\d+)\s*"
            r"\[(color=(?P<color>\w+)\s*)?"
            r"(max_drones=(?P<max_drones>\w+))?"
            r"\]$"
        ),
        'connection_patt': re.compile(
            r"^connection:\s+"
            r"(?P<start>[_a-zA-Z]+)"
            r"-(?P<end>[_a-zA-Z]+)\s*"
            r"(\[max_link_capacity=(?P<max_capacity>\w+)\])?$"
        )
    }

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.nb_drones = None
        self.network: dict = {
            'nb_drones': 0,
            'start_hub': {},
            'hubs': [],
            'end_hub': {},
            'connections': []
        }
        self.dispatch = {
            self.PATTERNS['nb_drones_patt']: self._handle_nb_drones,
            self.PATTERNS['start_hub_patt']: self._handle_start_hub,
            self.PATTERNS['hub_patt']: self._handle_hub,
            self.PATTERNS['end_hub_patt']: self._handle_end_hub,
            self.PATTERNS['connection_patt']: self._handle_connection,
        }

    def read_file(self) -> None:
        try:
            with open(self.file_path, 'r') as file:
                self.data = file.readlines()
        except FileNotFoundError:
            print(f"Error: the file {self.file_path} is not found")

    def parse(self) -> dict:
        if not self.data:
            raise ValueError("No data to parse. "
                             "Make sure you called read_file()")
        lines = [
            line.strip()
            for line in self.data
            if line.strip() and line[0] != '#'
        ]

        for line_n, line in enumerate(lines):
            if match := re.search(self.PATTERNS['nb_drones_patt'], line):
                self._handle_nb_drones(match.groupdict())
            elif match := re.search(self.PATTERNS['start_hub_patt'], line):
                self._handle_start_hub(match.groupdict())
            elif match := re.search(self.PATTERNS['hub_patt'], line):
                self._handle_hub(match.groupdict())
            elif match := re.search(self.PATTERNS['end_hub_patt'], line):
                print(match.groupdict())
                self._handle_end_hub(match.groupdict())
            elif match := re.search(self.PATTERNS['connection_patt'], line):
                self._handle_connection(match.groupdict())
            else:
                raise ValueError(f"Invalid input in line {line_n + 1}: \n{line}")
        return self.network

    def _handle_nb_drones(self, match: dict):
        self.network['nb_drones'] = int(match['nb_drones'])

    def _handle_start_hub(self, match: dict):
        self.network['start_hub']['name'] = match['name']
        self.network['start_hub']['coords'] = [int(match['x']), int(match['y'])]
        self.network['start_hub']['color'] = match['color']
        #must check if max_drones is equal to nb_drones

    def _handle_hub(self, match: dict):
        self.network['hubs'].append(
            {
                'name': match['name'],
                'coords': [int(match['x']), int(match['y'])],
                'color': match['color'],
                'max': int(match['max_drones']) if match['max_drones'] else 1
            }
        )

    def _handle_end_hub(self, match: dict):
        self.network['end_hub']['name'] = match['name']
        self.network['end_hub']['coords'] = [int(match['x']), int(match['y'])]
        self.network['end_hub']['color'] = match['color']   
        #must check if max_drones is equal to nb_drones

    def _handle_connection(self, match: dict):
        self.network['connections'].append(
            {
                'start': match['start'],
                'end': match['end'],
                'max': int(match['max_capacity']) if match['max_capacity'] else 1
            }
        )


parser = FileParser("02_simple_fork.txt")
parser.read_file()
try:
    result = parser.parse()
    print(result)
except ValueError as e:
    print(e)
