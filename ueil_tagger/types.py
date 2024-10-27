from enum import Enum, auto
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


class WardTaggingStrategy(Enum):
    FIELD = auto()
    ADDRESS = auto()
    ZIPCODE = auto()


@dataclass
class TaggingsSummary:
    taggings_deleted: int = 0
    taggings_added: int = 0
    members_modified: int = 0
    members_tagged_from_field: int = 0
    members_tagged_from_address: int = 0
    members_tagged_from_zipcode: int = 0
    members_not_tagged: int = 0

    def to_json(self) -> str:
        summary = {
            "taggings deleted": self.taggings_deleted,
            "taggings added": self.taggings_added,
            "members modified": self.members_modified,
            "members tagged from field": self.members_tagged_from_field,
            "members tagged from address": self.members_tagged_from_address,
            "members tagged from zipcode": self.members_tagged_from_zipcode,
            "members not tagged": self.members_not_tagged,
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

    def has_street_address(self) -> bool:
        if self.address_lines is None:
            return False
        if len(self.address_lines) == 0:
            return False
        if len(self.address_lines[0].strip()) <= 6:
            return False
        return True

    def full_address(self) -> Optional[str]:
        address_parts: list[str] = []
        if self.address_lines:
            address_parts += self.address_lines
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        address_str = ", ".join(address_parts)
        if self.zipcode:
            address_str += " " + str(self.zipcode)
        if len(address_str) > 0:
            return address_str
        return None
