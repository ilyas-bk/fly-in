import re
from typing import Any, Dict, Optional, Set


class FileParser:
    """Parse the custom network description format."""

    PATTERNS = {
        'nb_drones_patt': re.compile(
            r"^nb_drones:\s+(?P<nb_drones>\d+)$"
        ),
        'hub_patt': re.compile(
            r"^(?P<type>start_hub|hub|end_hub):\s+"
            r"(?P<name>[^\s-]+)\s+(?P<x>[-]?\d+)\s+(?P<y>[-]?\d+)"
            r"(?:\s+\[(?P<meta>.*)\])?$"
        ),
        'connection_patt': re.compile(
            r"^connection:\s+(?P<start>[^\s-]+)-(?P<end>[^\s-]+)"
            r"(?:\s+\[(?P<meta>.*)\])?$"
        ),
    }

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    def __init__(self, file_path: str):
        """Initialize the parser state for a file path."""
        self.file_path = file_path
        self.lines_raw: list[str] = list()

        self.defined_zones: Set[str] = set()
        self.existing_connections: Set[tuple[str, str]] = set()
        self.has_start_hub = False
        self.has_end_hub = False

        self.network: dict[str, Any] = {
            "nb_drones": 0,
            "start_hub": "",
            "end_hub": "",
            "zones": {},
        }

    def read_file(self) -> None:
        """Read the source file into memory."""
        try:
            with open(self.file_path, 'r') as file:
                self.lines_raw = file.readlines()
        except Exception:
            raise Exception(
                "Error: the file could not be read. "
                "Please check the file path and permissions."
            )

    def _parse_metadata(
        self, meta_string: Optional[str], context_line: int, is_zone: bool
    ) -> Dict[str, str]:
        """Parse key=value pairs inside brackets regardless of order."""
        valid_zone_keys = {"zone", "color", "max_drones"}
        valid_connection_keys = {"max_link_capacity"}
        metadata: Dict[str, str] = {}
        if not meta_string:
            return metadata

        metadata_parts = meta_string.split()
        for part in metadata_parts:
            if part.count('=') != 1:
                raise ValueError(
                    f"Parsing Error (Line {context_line}): "
                    "Metadata must be in key=value format."
                )
            if part.split('=')[1] == '':
                raise ValueError(
                    f"Parsing Error (Line {context_line}): "
                    "Metadata must be in key=value format."
                )

        pairs = re.findall(r'(\w+)=([^\s,\]]+)', meta_string)
        keys_in_pairs = {key for key, _ in pairs}
        if len(keys_in_pairs) != len(pairs):
            raise ValueError(
                f"Parsing Error (Line {context_line}): "
                "Duplicate metadata keys found."
            )

        for key, val in pairs:
            metadata[key] = val
        if is_zone and not \
                all(key in valid_zone_keys for key in metadata.keys()):
            raise ValueError(
                f"Parsing Error (Line {context_line}): "
                "Invalid metadata key(s) found."
            )
        if not is_zone and not \
                all(key in valid_connection_keys for key in metadata.keys()):
            raise ValueError(
                f"Parsing Error (Line {context_line}): "
                "Invalid metadata key(s) found."
            )
        return metadata

    def parse(self) -> dict[str, Any]:
        """Parse the previously read file into a network dictionary."""
        if not self.lines_raw:
            raise ValueError(
                "No data to parse. Make sure you called "
                "read_file() and the file is not empty."
            )

        first_meaningful_line = True

        for idx, raw_line in enumerate(self.lines_raw):
            line_num = idx + 1
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "#" in line:
                line = line.split("#")[0].strip()

            if first_meaningful_line:
                if match := self.PATTERNS["nb_drones_patt"].match(line):
                    val = int(match.group("nb_drones"))
                    if val <= 0:
                        raise ValueError(
                            f"Parsing Error (Line {line_num}): "
                            "nb_drones must be a positive integer."
                        )
                    self.network["nb_drones"] = val
                    first_meaningful_line = False
                    continue
                else:
                    raise ValueError(
                        f"Parsing Error (Line {line_num}): The first "
                        "configuration line must define 'nb_drones'."
                    )

            if match := self.PATTERNS["hub_patt"].match(line):
                self._handle_hub(match.groupdict(), line_num)

            elif match := self.PATTERNS["connection_patt"].match(line):
                self._handle_connection(match.groupdict(), line_num)

            else:
                raise ValueError(
                    f"Parsing Error (Line {line_num}): "
                    "Syntactically invalid line framework.\n"
                    f"-> \"{line}\""
                )

        if not self.has_start_hub:
            raise ValueError(
                "Parsing Error: Missing exactly one "
                "'start_hub' definitions."
            )
        if not self.has_end_hub:
            raise ValueError(
                "Parsing Error: Missing exactly one "
                "'end_hub' definitions."
            )

        return self.network

    def _handle_hub(self, match_groups: dict[str, str], line_num: int) -> None:
        """Process a hub definition line."""
        h_type = match_groups["type"]
        name = match_groups["name"]

        if name in self.defined_zones:
            raise ValueError(
                f"Parsing Error (Line {line_num}): "
                f"Zone name '{name}' has already been defined."
            )

        metadata = self._parse_metadata(match_groups["meta"], line_num, True)

        zone_type = metadata.get("zone", "normal")
        if zone_type not in self.VALID_ZONE_TYPES:
            raise ValueError(
                f"Parsing Error (Line {line_num}): "
                f"Invalid zone type '{zone_type}'."
            )

        max_drones = 1
        if "max_drones" in metadata:
            try:
                max_drones = int(metadata["max_drones"])
                if max_drones <= 0:
                    raise ValueError()
            except ValueError as exc:
                raise ValueError(
                    f"Parsing Error (Line {line_num}): "
                    "'max_drones' must be a positive integer."
                ) from exc

        zone_color = metadata.get("color", None)
        if zone_color is not None:
            if not zone_color.isalpha():
                raise ValueError(
                    f"Parsing Error (Line {line_num}): "
                    "'color' must be a string of alphabetic characters."
                )

        hub_data: dict[str, Any] = {
            "coords": [int(match_groups["x"]), int(match_groups["y"])],
            "zone_type": zone_type,
            "color": zone_color,
            "max_drones": max_drones,
            "current_drones": 0,
            "neighbors": {},
            "connections": {},
        }

        self.network["zones"][name] = hub_data

        if h_type == "start_hub":
            if self.has_start_hub:
                raise ValueError(
                    f"Parsing Error (Line {line_num}): "
                    "Duplicate start_hub discovered."
                )
            self.has_start_hub = True
            self.network["start_hub"] = name
        elif h_type == "end_hub":
            if self.has_end_hub:
                raise ValueError(
                    f"Parsing Error (Line {line_num}): "
                    "Duplicate end_hub discovered."
                )
            self.has_end_hub = True
            self.network["end_hub"] = name

        self.defined_zones.add(name)

    def _handle_connection(
        self,
        match_groups: dict[str, str],
        line_num: int,
    ) -> None:
        """Process a connection definition line."""
        start = match_groups["start"]
        end = match_groups["end"]

        if start not in self.defined_zones:
            raise ValueError(
                f"Parsing Error (Line {line_num}): "
                f"Origin zone '{start}' is not defined yet."
            )
        if end not in self.defined_zones:
            raise ValueError(
                f"Parsing Error (Line {line_num}): "
                f"Destination zone '{end}' is not defined yet."
            )

        if start == end:
            raise ValueError(
                f"Parsing Error (Line {line_num}): "
                "Self-connections are not allowed."
            )

        connection_pair: tuple[str, str]
        if start <= end:
            connection_pair = (start, end)
        else:
            connection_pair = (end, start)
        if connection_pair in self.existing_connections:
            raise ValueError(
                f"Parsing Error (Line {line_num}): "
                f"Duplicate connection '{start}-{end}' discovered."
            )

        metadata = self._parse_metadata(match_groups["meta"], line_num, False)

        max_capacity = 1
        if "max_link_capacity" in metadata:
            try:
                max_capacity = int(metadata["max_link_capacity"])
                if max_capacity <= 0:
                    raise ValueError()
            except ValueError as exc:
                raise ValueError(
                    f"Parsing Error (Line {line_num}): "
                    "'max_link_capacity' must be a positive integer."
                ) from exc

        start_cost = 1.0
        if self.network["zones"][start]["zone_type"] == "restricted":
            start_cost = 2.0
        elif self.network["zones"][start]["zone_type"] == "priority":
            start_cost = 0.9

        end_cost = 1.0
        if self.network["zones"][end]["zone_type"] == "restricted":
            end_cost = 2.0
        elif self.network["zones"][end]["zone_type"] == "priority":
            end_cost = 0.9

        self.network["zones"][start]["neighbors"][end] = end_cost
        self.network["zones"][end]["neighbors"][start] = start_cost

        self.network["zones"][start]["connections"][end] = [max_capacity, 0]
        self.network["zones"][end]["connections"][start] = [max_capacity, 0]

        self.existing_connections.add(connection_pair)
