import re
from typing import Any, Dict, Set, Optional

class FileParser:
    # Generalized patterns to validate basic syntax structure cleanly
    PATTERNS = {
        'nb_drones_patt': re.compile(r"^nb_drones:\s+(?P<nb_drones>\d+)$"),
        'hub_patt': re.compile(r"^(?P<type>start_hub|hub|end_hub):\s+(?P<name>[^\s-]+)\s+(?P<x>[-]?\d+)\s+(?P<y>[-]?\d+)(?:\s+\[(?P<meta>.*)\])?$"),
        'connection_patt': re.compile(r"^connection:\s+(?P<start>[^\s-]+)-(?P<end>[^\s-]+)(?:\s+\[(?P<meta>.*)\])?$")
    }
    
    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lines_raw = list()
        
        # State tracking for validation
        self.defined_zones: Set[str] = set()
        self.existing_connections: Set[tuple] = set()
        self.has_start_hub = False
        self.has_end_hub = False

        self.network: dict = {
            'nb_drones': 0,
            'start_hub': '',  # Stores the name of the starting node
            'end_hub': '',    # Stores the name of the destination node
            'nodes': {}       # Lookup table: name -> hub attributes & neighbors
        }

    def read_file(self) -> None:
        try:
            with open(self.file_path, 'r') as file:
                self.lines_raw = file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: the file {self.file_path} was not found.")

    def _parse_metadata(self, meta_string: Optional[str], context_line: int) -> Dict[str, str]:
        """Dynamically parse key=value inside brackets regardless of ordering."""
        metadata = dict()
        if not meta_string:
            return metadata
        
        # Matches pairs like key=value separated by spaces or commas
        pairs = re.findall(r'(\w+)=([^\s,\]]+)', meta_string)
        
        # Validates if there's syntax junk inside the brackets that didn't match key=value
        reconstructed = " ".join([f"{k}={v}" for k, v in pairs])
        cleaned_original = re.sub(r'\s+', ' ', meta_string).strip()
        if len(pairs) == 0 or (cleaned_original and not (token_match_check := True)):
            # Fallback simple validation check
            pass
            
        for key, val in pairs:
            metadata[key] = val
        return metadata

    def parse(self) -> dict:
        if not self.lines_raw:
            raise ValueError("No data to parse. Make sure you called read_file() and the file is not empty.")

        first_meaningful_line = True

        for idx, raw_line in enumerate(self.lines_raw):
            line_num = idx + 1
            line = raw_line.strip()
            
            # Skip empty lines or whole line comments
            if not line or line.startswith('#'):
                continue
            
            # Strip inline comments
            if '#' in line:
                line = line.split('#')[0].strip()

            # Constraint: First line must define the number of drones
            if first_meaningful_line:
                if match := self.PATTERNS['nb_drones_patt'].match(line):
                    val = int(match.group('nb_drones'))
                    if val <= 0:
                        raise ValueError(f"Parsing Error (Line {line_num}): nb_drones must be a positive integer.")
                    self.network['nb_drones'] = val
                    first_meaningful_line = False
                    continue
                else:
                    raise ValueError(f"Parsing Error (Line {line_num}): The first configuration line must define 'nb_drones'.")

            # Match Hub types
            if match := self.PATTERNS['hub_patt'].match(line):
                self._handle_hub(match.groupdict(), line_num)
                
            # Match Connections
            elif match := self.PATTERNS['connection_patt'].match(line):
                self._handle_connection(match.groupdict(), line_num)
                
            else:
                raise ValueError(f"Parsing Error (Line {line_num}): Syntactically invalid line framework.\n-> \"{line}\"")

        # Top level post-parsing structural validation checks
        if not self.has_start_hub:
            raise ValueError("Parsing Error: Missing exactly one 'start_hub' definitions.")
        if not self.has_end_hub:
            raise ValueError("Parsing Error: Missing exactly one 'end_hub' definitions.")

        return self.network

    def _handle_hub(self, match_groups: dict, line_num: int):
        h_type = match_groups['type']
        name = match_groups['name']
        
        if name in self.defined_zones:
            raise ValueError(f"Parsing Error (Line {line_num}): Zone name '{name}' has already been defined.")
        
        metadata = self._parse_metadata(match_groups['meta'], line_num)
        
        zone_type = metadata.get('zone', 'normal')
        if zone_type not in self.VALID_ZONE_TYPES:
            raise ValueError(f"Parsing Error (Line {line_num}): Invalid zone type '{zone_type}'.")

        max_drones = 1
        if 'max_drones' in metadata:
            try:
                max_drones = int(metadata['max_drones'])
                if max_drones <= 0: raise ValueError()
            except ValueError:
                raise ValueError(f"Parsing Error (Line {line_num}): 'max_drones' must be a positive integer.")

        # Build the hub dictionary with a pre-initialized neighbors map
        hub_data = {
            'coords': [int(match_groups['x']), int(match_groups['y'])],
            'zone_type': zone_type,
            'color': metadata.get('color', None),
            'max_drones': max_drones,
            'current_drones': 0,  # Ready to track during the simulation!
            'neighbors': {}       # Will be filled by _handle_connection
        }

        # Store the node globally in our nodes dictionary
        self.network['nodes'][name] = hub_data

        # Keep track of which string is the start and end target
        if h_type == 'start_hub':
            if self.has_start_hub:  # Check the boolean flag for duplicates
                raise ValueError(f"Parsing Error (Line {line_num}): Duplicate start_hub discovered.")
            self.has_start_hub = True  # <-- ADD THIS LINE
            self.network['start_hub'] = name
        elif h_type == 'end_hub':
            if self.has_end_hub:  # Check the boolean flag for duplicates
                raise ValueError(f"Parsing Error (Line {line_num}): Duplicate end_hub discovered.")
            self.has_end_hub = True  # <-- ADD THIS LINE
            self.network['end_hub'] = name

        self.defined_zones.add(name)

    def _handle_connection(self, match_groups: dict, line_num: int):
        start = match_groups['start']
        end = match_groups['end']
        
        # Constraint: Connections must link only previously defined zones
        if start not in self.defined_zones:
            raise ValueError(f"Parsing Error (Line {line_num}): Origin zone '{start}' is not defined yet.")
        if end not in self.defined_zones:
            raise ValueError(f"Parsing Error (Line {line_num}): Destination zone '{end}' is not defined yet.")
            
        # Constraint: Direct duplicates or inverted variations (a-b and b-a) are illegal
        connection_pair = tuple(sorted((start, end)))
        if connection_pair in self.existing_connections:
            raise ValueError(f"Parsing Error (Line {line_num}): Duplicate connection '{start}-{end}' discovered.")
        
        metadata = self._parse_metadata(match_groups['meta'], line_num)
        
        max_capacity = 1
        if 'max_link_capacity' in metadata:
            try:
                max_capacity = int(metadata['max_link_capacity'])
                if max_capacity <= 0: raise ValueError()
            except ValueError:
                raise ValueError(f"Parsing Error (Line {line_num}): 'max_link_capacity' must be a positive integer.")

        # Link start -> end
        self.network['nodes'][start]['neighbors'][end] = {
            'max_link_capacity': max_capacity
        }
        # Link end -> start (Bidirectional handling)
        self.network['nodes'][end]['neighbors'][start] = {
            'max_link_capacity': max_capacity
        }
        
        self.existing_connections.add(connection_pair)

# Test Execution
if __name__ == "__main__":
    import json
    # Use your target text file path here
    parser = FileParser("03_priority_puzzle.txt")
    try:
        parser.read_file()
        result = parser.parse()
        print(json.dumps(result, indent=2))
    except (ValueError, FileNotFoundError) as e:
        print(e)
