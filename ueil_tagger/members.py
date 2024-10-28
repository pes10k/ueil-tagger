from __future__ import annotations

from datetime import datetime
import json
import logging
from typing import Optional, TYPE_CHECKING

from ueil_tagger.client import Client
from ueil_tagger.types import Member, TaggingsSummary, WardTaggingStrategy
from ueil_tagger.wards import get_ward_id_to_uuid_map, wards_for_member

if TYPE_CHECKING:
    from ueil_tagger.types import Uuid, WardNum, ZipCode, WardToTagMap
    from ueil_tagger.types import WebAPIRecord


def field_to_zip(field: Optional[str]) -> Optional[ZipCode]:
    if not field:
        return None
    if len(field) > 5:
        field = field[0:5]

    try:
        return int(field)
    except ValueError:
        pass
    return None


def uuid_for_member_record(record: WebAPIRecord) -> Optional[Uuid]:
    if "identifiers" not in record:
        return None
    for identifier_record in record["identifiers"]:
        if not identifier_record.startswith("action_network:"):
            continue
        return str(identifier_record.replace("action_network:", ""))
    return None


def get_member_from_record(record: WebAPIRecord) -> Optional[Member]:
    record_uuid = uuid_for_member_record(record)
    if not record_uuid:
        logging.error("Unable to find an action network identifier for "
                        "record:\n%s", json.dumps(record))
        return None

    if "postal_addresses" not in record:
        return None

    custom_field_ward = None
    try:
        custom_field_int = int(record["custom_fields"]["Aldermanic Ward"])
        if 0 < custom_field_int <= 50:
            custom_field_ward = custom_field_int
    except ValueError:
        logging.error(
            "person=%s: Unexpected value for 'Aldermanic Ward' field, '%s'",
            record_uuid, record["custom_fields"]["Aldermanic Ward"])
    except KeyError:
        pass

    address = record["postal_addresses"][0]
    possible_zipcode = address.get("postal_code")
    zipcode = field_to_zip(possible_zipcode)

    member = Member(record_uuid, address.get("address_lines"),
        address.get("locality"), address.get("region"),
        zipcode, custom_field_ward)
    return member


def get_members_updated_since(client: Client,
                              since: Optional[datetime] = None) -> list[Member]:
    members = []
    page_index = 1
    while True:
        logging.info("Requesting people records, page=%s", page_index)
        people_response = client.get_people(page_index, since)
        records = people_response["_embedded"]["osdi:people"]

        logging.info("...received %s additional records", len(records))
        if len(records) == 0:
            break

        for record in records:
            member = get_member_from_record(record)
            if not member:
                logging.error("Unable to parse API response as a member:\n%s",
                              json.dumps(record))
                continue

            if since:
                modified_date = record["modified_date"]
                modified_date = datetime.fromisoformat(modified_date)
                if modified_date < since:
                    raise ValueError("Unexpected person result\n"
                                     f"person={member.identifier}: was updated "
                                     f"after the given date '{modified_date}'")
            members.append(member)
        page_index += 1
    return members


def clear_ward_tags_from_member(client: Client, member: Member,
                                ward_to_tag_map: WardToTagMap) -> int:
    ward_tag_uuids = ward_to_tag_map.values()
    taggings_for_member = client.get_taggings_for_person(member.identifier)
    ward_tags_for_member = set(ward_tag_uuids) & set(taggings_for_member)

    num_tags_removed = 0
    for tag_uuid in ward_tags_for_member:
        logging.info("person=%s: removing tagging %s",
                     member.identifier, tag_uuid)
        client.delete_tagging_for_person(tag_uuid, member.identifier)
        num_tags_removed += 1
    return num_tags_removed


def set_ward_tags_for_member_uuid(
        client: Client, person_uuid: Uuid, min_sqft: int,
        summary: Optional[TaggingsSummary] = None) -> tuple[bool, TaggingsSummary]:
    if not summary:
        summary = TaggingsSummary()
    result = client.get_person(person_uuid)
    member = get_member_from_record(result)
    if not member:
        logging.error("Unable to load a person result for uuid=%s",
                      person_uuid)
        return False, summary
    ward_to_tag_map = get_ward_id_to_uuid_map(client)
    set_ward_tags_for_member(client, member, min_sqft, ward_to_tag_map,
                             summary)
    return True, summary


def set_ward_tags_for_member(
        client: Client, member: Member, min_sqft: int,
        ward_to_tag_map: Optional[WardToTagMap] = None,
        summary: Optional[TaggingsSummary] = None) -> TaggingsSummary:
    if not summary:
        summary = TaggingsSummary()
    if not ward_to_tag_map:
        ward_to_tag_map = get_ward_id_to_uuid_map(client)

    num_tagggings_removed = clear_ward_tags_from_member(client, member,
                                                        ward_to_tag_map)
    summary.taggings_deleted += num_tagggings_removed
    ward_result = wards_for_member(member, min_sqft)

    if not ward_result:
        summary.members_not_tagged += 1
        if num_tagggings_removed > 0:
            summary.members_modified += 1
        logging.info("person=%s: not tagging to any wards",
                        member.identifier)
        return summary

    wards, strategy = ward_result
    match strategy:
        case WardTaggingStrategy.FIELD:
            summary.members_tagged_from_field += 1
        case WardTaggingStrategy.ADDRESS:
            summary.members_tagged_from_address += 1
        case WardTaggingStrategy.ZIPCODE:
            summary.members_tagged_from_zipcode += 1

    for ward in wards:
        ward_tag_uuid = ward_to_tag_map[ward]
        client.set_tagging_for_person(ward_tag_uuid, member.identifier)
        logging.info("person=%s: tagging to ward=%s (%s)",
                        member.identifier, ward_tag_uuid, ward)
        summary.taggings_added += 1
    summary.members_modified += 1
    return summary


def set_ward_tags_for_all_members_since(
        client: Client, min_sqft: int,
        since: Optional[datetime] = None) -> TaggingsSummary:
    summary = TaggingsSummary()
    if since:
        logging.info("Tagging members updated since %s", since.isoformat())
    else:
        logging.info("Tagging all members")

    ward_to_tag_map = get_ward_id_to_uuid_map(client)
    members = get_members_updated_since(client, since)
    for member in members:
        set_ward_tags_for_member(client, member, min_sqft, ward_to_tag_map,
                                 summary)
    return summary
