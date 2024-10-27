from dataclasses import dataclass
import json
from typing import Optional


@dataclass
class Coords:
    lat: float
    long: float


ConfigSettings = dict[str, str | float]
Uuid = str
WardNum = int
ZipCode = int

WardZipData = dict[ZipCode, list[tuple[WardNum, float]]]
SigWardZipData = dict[ZipCode, list[WardNum]]


@dataclass
class TaggingsSummary:
    taggings_deleted: int = 0
    taggings_added: int = 0
    members_modified: int = 0
    members_tagged: int = 0

    def to_json(self) -> str:
        summary = {
            "taggings deleted": self.taggings_deleted,
            "taggings added": self.taggings_added,
            "members modified": self.members_modified,
            "members tagged": self.members_tagged,
        }
        return json.dumps(summary)


@dataclass
class Member:
    identifier: Uuid
    address_lines: Optional[list[str]]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[int]
    custom_field_ward: Optional[int]

    def full_address(self) -> Optional[str]:
        address_parts = []
        if self.address_lines:
            address_parts += self.address_lines
        if self.city:
            address_parts += self.city
        if self.state:
            address_parts += self.state
        address_str = ", ".join(address_parts)
        if self.zipcode:
            address_str += " " + str(self.zipcode)
        if len(address_str) > 0:
            return address_str
        return None
