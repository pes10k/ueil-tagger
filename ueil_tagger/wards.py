from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pprint import pformat
from typing import cast, Optional, TYPE_CHECKING

from shapely import Point
import shapely.wkt

from ueil_tagger import DATA_DIR_PATH
from ueil_tagger.client import Client
from ueil_tagger.geolocate import coords_for_address
from ueil_tagger.types import Member, WardTaggingStrategy

if TYPE_CHECKING:
    from shapely import MultiPolygon
    from ueil_tagger.types import Uuid, WardNum, ZipCode
    from ueil_tagger.types import WardZipData, SigWardZipData, WardToTagMap


@dataclass
class WardShape:
    ward: WardNum
    shape: MultiPolygon


def load_ward_data() -> list[WardShape]:
    ward_data_path = DATA_DIR_PATH / "wards.json"
    ward_records = json.loads(ward_data_path.read_text())

    wards = []
    for ward_number, ward_shape_text in ward_records:
        ward_number = int(ward_number)
        ward_shape = cast("MultiPolygon", shapely.wkt.loads(ward_shape_text))
        ward = WardShape(ward_number, ward_shape)
        wards.append(ward)
    return wards


def load_wards_for_zip_data() -> WardZipData:
    ward_data_path = DATA_DIR_PATH / "zipcode_to_wards.json"
    data = json.loads(ward_data_path.read_text())
    ward_zip_data: WardZipData = {}
    for key, value in data.items():
        ward_zip_data[int(key)] = value
    return ward_zip_data


def significant_wards_for_zip(min_ward_sqft: int) -> SigWardZipData:
    wards_for_zip = load_wards_for_zip_data()
    sig_wards_for_zip: SigWardZipData = {}
    for zipcode, wards in wards_for_zip.items():
        sig_wards_for_zip[zipcode] = []
        for ward_num, sqft_overlap in wards:
            if sqft_overlap >= min_ward_sqft:
                sig_wards_for_zip[zipcode].append(ward_num)
    return sig_wards_for_zip


def ward_for_address(address: str) -> Optional[WardNum]:
    coords = coords_for_address(address)
    if not coords:
        return None
    point = Point(coords.long, coords.lat)
    ward_data = load_ward_data()
    for ward in ward_data:
        if ward.shape.contains(point):
            return ward.ward
    return None


def wards_for_member(member: Member,
                     min_ward_sqft: int) -> Optional[tuple[list[WardNum], WardTaggingStrategy]]:
    sig_wards_for_zip = significant_wards_for_zip(min_ward_sqft)
    ward: int | None = None
    if member.custom_field_ward:
        ward = member.custom_field_ward
        logging.debug("person=%s: assigned ward '%s' based on custom field",
                      member.identifier, ward)
        return ([ward], WardTaggingStrategy.FIELD)
    if member.has_street_address():
        member_address = member.full_address()
        if member_address:
            ward = ward_for_address(member_address)
            if ward:
                logging.debug("person=%s: assigned ward '%s' by geocoding '%s'",
                              member.identifier, ward, member_address)
                return ([ward], WardTaggingStrategy.ADDRESS)
            logging.error("person=%s: couldn't geocode ward from address '%s'",
                          member.identifier, member_address)
    if member.zipcode:
        if member.zipcode in sig_wards_for_zip:
            wards = sig_wards_for_zip[member.zipcode]
            logging.debug("person=%s: assigned wards '%s' based on zip '%s'",
                          member.identifier, json.dumps(wards), member.zipcode)
            return (wards, WardTaggingStrategy.ZIPCODE)
    logging.debug("person=%s: unable to assign a ward", member.identifier)
    return None


def get_ward_id_to_uuid_map(client: Client) -> WardToTagMap:
    ward_tags: WardToTagMap = {}
    page_index = 1
    while len(ward_tags) < 50:
        tag_response = client.get_tags(page_index)
        for tag in tag_response["_embedded"]["osdi:tags"]:
            tag_name = tag["name"]
            if not tag_name.startswith("Chicago Ward "):
                continue
            ward_num = int(tag_name.replace("Chicago Ward ", ""))
            if ward_num > 50 or ward_num < 1:
                continue
            tag_uuid = tag["identifiers"][0].replace("action_network:", "")
            ward_tags[ward_num] = tag_uuid

        if page_index == tag_response["total_pages"]:
            break
        page_index += 1

    num_tags = len(ward_tags)
    if num_tags != 50:
        msg = f"Found unexpected number of ward tags: {num_tags}"
        logging.error(msg)
        raise ValueError(msg)
    logging.debug("Successfully found 50 ward tags in the database: %s",
                  pformat(ward_tags))
    return ward_tags
