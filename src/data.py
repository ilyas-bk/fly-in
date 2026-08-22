from __future__ import annotations

import sys
from typing import Any

from src.parser import FileParser


class Network:
    """Represent a parsed network configuration."""

    def __init__(self, network: dict[str, Any]) -> None:
        """Store the raw network and its drone count."""
        self.network = network
        self.nb_drones = int(network["nb_drones"])

    def update(self, network: dict[str, Any]) -> dict[str, Any]:
        """Update the boundary zones to match the drone capacity."""
        metadata = network
        first_zone = next(iter(metadata["zones"]))
        last_zone = next(reversed(metadata["zones"]))
        metadata["zones"][first_zone]["max_drones"] = self.nb_drones
        metadata["zones"][last_zone]["max_drones"] = self.nb_drones
        return metadata

    @staticmethod
    def parse(file: str) -> dict[str, Any]:
        """Parse a network definition from the given file."""
        parser = FileParser(file)
        network: dict[str, Any] = {}
        try:
            parser.read_file()
            network = parser.parse()
            metadata = Network(network)
            network = metadata.update(network)
        except (ValueError, FileNotFoundError) as exc:
            print(exc)
            sys.exit(1)

        return network


class Drone:
    """Represent a drone moving through the network."""

    _id_counter = 1

    def __init__(self, start: str) -> None:
        """Create a drone at the given starting position."""
        self.id = Drone._id_counter
        Drone._id_counter += 1
        self.path_idx = 0
        self.position = start
        self.path: list[str] = []
        self.wait = 0
        self.connection_from: str | None = None
        self.connection_to: str | None = None

    @staticmethod
    def init_drones(nb_drones: int) -> list["Drone"]:
        """Create the requested number of drones."""
        return [Drone("start") for _ in range(nb_drones)]


class Zone:
    """Represent a zone in the parsed network."""

    def __init__(self, zone: dict[str, Any], name: str) -> None:
        """Create a zone wrapper from parsed zone data."""
        self.name = name
        self.coords = zone["coords"]
        self.color = zone["color"]
        self.curr_drones = zone["current_drones"]
        self.capacity = zone["max_drones"]
        self.neighbors = zone["neighbors"]
        self.connections = zone["connections"]
        self.type = zone["zone_type"]

    @staticmethod
    def init_zones(network: dict[str, Any]) -> dict[str, "Zone"]:
        """Build a mapping of zone names to ``Zone`` instances."""
        return {
            name: Zone(data, name)
            for name, data in network["zones"].items()
        }
