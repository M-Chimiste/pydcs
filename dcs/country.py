from __future__ import annotations

import random
from typing import List, Dict, Set, Type, Tuple

from dcs.helicopters import HelicopterType
from dcs.planes import PlaneType
from dcs.unitgroup import VehicleGroup, ShipGroup, PlaneGroup, StaticGroup, HelicopterGroup, FlyingGroup, Group


def find_exact(group_name, find_name):
    return group_name == find_name


def find_match(group_name, find_name):
    return find_name in group_name


find_map = {
    "exact": find_exact,
    "match": find_match
}


class Country:
    callsign: Dict[str, List[str]] = {}
    planes: List[Type[PlaneType]] = []
    helicopters: List[Type[HelicopterType]] = []

    def __init__(self, _id, name, short_name):
        self.id = _id
        self.name = name
        self.shortname = short_name
        self.vehicle_group: List[VehicleGroup] = []
        self.ship_group: List[ShipGroup] = []
        self.plane_group: List[PlaneGroup] = []
        self.helicopter_group: List[HelicopterGroup] = []
        self.static_group: List[StaticGroup] = []
        self.current_callsign_id = 99
        self.callsign_numbers: Dict[str, Set[int]] = {}
        self._tail_numbers: Set[str] = set()

    def add_vehicle_group(self, vgroup) -> None:
        self.vehicle_group.append(vgroup)

    def add_ship_group(self, sgroup):
        self.ship_group.append(sgroup)

    def add_plane_group(self, pgroup):
        self.plane_group.append(pgroup)

    def add_helicopter_group(self, hgroup):
        self.helicopter_group.append(hgroup)

    def add_aircraft_group(self, group: FlyingGroup) -> None:
        if group.units[0].unit_type.helicopter:
            assert isinstance(group, HelicopterGroup)
            self.helicopter_group.append(group)
        else:
            assert isinstance(group, PlaneGroup)
            self.plane_group.append(group)

    def add_static_group(self, sgroup):
        self.static_group.append(sgroup)

    def remove_static_group(self, sgroup):
        for i in range(0, len(self.static_group)):
            if sgroup.id == self.static_group[i].id:
                del self.static_group[i]
                return True

        return False

    def find_group(self, group_name, search="exact"):
        groups = [self.vehicle_group,
                  self.ship_group,
                  self.plane_group,
                  self.helicopter_group,
                  self.static_group]
        for search_group in groups:
            for group in search_group:
                if find_map[search](group.name, group_name):
                    return group
        return None

    def find_vehicle_group(self, name: str, search="exact"):
        for group in self.vehicle_group:
            if find_map[search](group.name, name):
                return group
        return None

    def find_ship_group(self, name: str, search="exact"):
        for group in self.ship_group:
            if find_map[search](group.name, name):
                return group
        return None

    def find_plane_group(self, name: str, search="exact"):
        for group in self.plane_group:
            if find_map[search](group.name, name):
                return group

    def find_helicopter_group(self, name: str, search="exact"):
        for group in self.helicopter_group:
            if find_map[search](group.name, name):
                return group

    def find_static_group(self, name: str, search="exact"):
        for group in self.static_group:
            if find_map[search](group.name, name):
                return group
        return None

    def vehicle_group_within(self, point, distance) -> List[Group]:
        """Return all vehicle groups within the radius of a given point.

        Args:
            point(mapping.Point): Center of circle
            distance: Distance to the point

        Returns:
            Sequence of vehicle groups within range.
        """
        return [x for x in self.vehicle_group if x.position.distance_to_point(point) < distance]

    def static_group_within(self, point, distance) -> List[Group]:
        """Return all static groups within the radius of a given point.

        Args:
            point(mapping.Point): Center of circle
            distance: Distance to the point

        Returns:
            Sequence of static groups within range.
        """
        return [x for x in self.static_group if x.position.distance_to_point(point) < distance]

    def next_callsign_id(self):
        self.current_callsign_id += 1
        return self.current_callsign_id

    def next_callsign_category(self, category, callnames) -> Tuple[str, int]:
        callsigns = [
            callsign
            for callsign in self.callsign[category] + callnames
            if not self.callsign_numbers.get(callsign) or len(self.callsign_numbers[callsign]) < 9
        ]
        if not callsigns:
            # Everything's fully booked, start from scratch...
            self.callsign_numbers = {}
            return self.next_callsign_category(category, callnames)
        callsign = random.choice(callsigns)
        taken = self.callsign_numbers.get(callsign)
        numbers = set(range(1, 10))
        if taken:
            numbers -= taken
        else:
            self.callsign_numbers[callsign] = set()

        number = random.choice(tuple(numbers))
        self.callsign_numbers[callsign].add(number)
        return str(callsign), number

    @property
    def unused_onboard_numbers(self) -> Set[str]:
        return {"{:03}".format(x) for x in range(10, 1000)} - self._tail_numbers

    def reset_onboard_numbers(self):
        """
        Resets/clears reserved onboard numbers for this country.
        :return:
        """
        self._tail_numbers = set()

    def reserve_onboard_num(self, number: str) -> bool:
        """
        Reserve the give onboard_num (tail number), if already used return True.
        :param int number: onboard num
        :return: True if number is already in use, else False
        """
        is_in = number in self._tail_numbers
        self._tail_numbers.add(number)
        return is_in

    def next_onboard_num(self) -> str:
        free_set = self.unused_onboard_numbers
        if free_set:
            tailnum = free_set.pop()
            self.reserve_onboard_num(tailnum)
            return tailnum
        return random.choice(sorted(self._tail_numbers))

    def dict(self):
        d = {
            "name": self.name,
            "id": self.id
        }

        if self.vehicle_group:
            d["vehicle"] = {"group": {}}
            i = 1
            for vgroup in self.vehicle_group:
                d["vehicle"]["group"][i] = vgroup.dict()
                i += 1

        if self.ship_group:
            d["ship"] = {"group": {}}
            i = 1
            for group in self.ship_group:
                d["ship"]["group"][i] = group.dict()
                i += 1

        if self.plane_group:
            d["plane"] = {"group": {}}
            i = 1
            for plane_group in self.plane_group:
                d["plane"]["group"][i] = plane_group.dict()
                i += 1

        if self.helicopter_group:
            d["helicopter"] = {"group": {}}
            i = 1
            for group in self.helicopter_group:
                d["helicopter"]["group"][i] = group.dict()
                i += 1

        if self.static_group:
            d["static"] = {"group": {}}
            i = 1
            for static_group in self.static_group:
                d["static"]["group"][i] = static_group.dict()
                i += 1
        return d

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Country):
            return False
        return self.id == other.id

    def __str__(self):
        return str(self.id) + "," + self.name + "," + str(self.vehicle_group)

    def __hash__(self) -> int:
        return hash(self.id)
