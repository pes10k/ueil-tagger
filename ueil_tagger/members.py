from __future__ import annotations

from datetime import datetime
import logging
from typing import Optional, TYPE_CHECKING

from ueil_tagger.client import Client
from ueil_tagger.types import Member, TaggingsSummary
from ueil_tagger.wards import get_ward_id_to_uuid_mapping, wards_for_member

if TYPE_CHECKING:
    from ueil_tagger.types import Uuid, WardNum


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
            record_uuid = record["identifiers"][0].replace("action_network:", "")
            if since:
                modified_date = record["modified_date"]
                logging.debug("person=%s: not updated since '%s'",
                              record_uuid, modified_date)
                modified_date = datetime.fromisoformat(modified_date)
                if modified_date < since:
                    continue
            address_lines = None
            city = None
            state = None
            zipcode = None
            custom_field_ward = None

            if "postal_addresses" in record:
                address = record["postal_addresses"][0]
                address_lines = address.get("address_lines")
                city = address.get("locality")
                state = address.get("region")
                zipcode = address.get("postal_code")
                if zipcode and len(zipcode) > 5:
                    zipcode = zipcode[0:5]

                try:
                    custom_field_ward = int(record["custom_fields"]["Aldermanic Ward"])
                except KeyError:
                    pass
                except ValueError:
                    logging.error(
                        "person=%s: Unexpected value for 'Aldermanic Ward' field, '%s'",
                        record_uuid, record["custom_fields"]["Aldermanic Ward"])

            members.append(Member(record_uuid, address_lines, city, state,
                                  zipcode, custom_field_ward))
        page_index += 1
    return members


def clear_ward_tags_from_member(client: Client, member: Member,
                                ward_id_uuid_map: dict[WardNum, Uuid]) -> int:
    ward_tag_uuids = ward_id_uuid_map.values()
    taggings_for_member = client.get_taggings_for_person(member.identifier)
    ward_tags_for_member = set(ward_tag_uuids) & set(taggings_for_member)

    num_tags_removed = 0
    for tag_uuid in ward_tags_for_member:
        logging.info("person=%s: removing tagging %s",
                     member.identifier, tag_uuid)
        client.delete_tagging_for_person(tag_uuid, member.identifier)
        num_tags_removed += 1
    return num_tags_removed


def set_ward_tags_for_all_members_since(
        client: Client, min_sqft: int,
        since: Optional[datetime] = None) -> TaggingsSummary:
    summary = TaggingsSummary()
    if since:
        logging.info("Tagging members updated since %s", since.isoformat())
    else:
        logging.info("Tagging all members")

    ward_id_uuid_map = get_ward_id_to_uuid_mapping(client)
    members = get_members_updated_since(client, since)
    for member in members:
        tagggings_removed = clear_ward_tags_from_member(client, member,
                                                        ward_id_uuid_map)
        summary.taggings_deleted = tagggings_removed
        wards = wards_for_member(member, min_sqft)
        if not wards:
            if tagggings_removed > 0:
                summary.members_modified += 1
            logging.info("person=%s: not tagging to any wards",
                         member.identifier)
            continue

        for ward in wards:
            ward_tag_uuid = ward_id_uuid_map[ward]
            client.set_tagging_for_person(ward_tag_uuid, member.identifier)
            logging.info("person=%s: tagging to ward=%s (%s)",
                         member.identifier, ward_tag_uuid, ward)
            summary.taggings_added += 1
        summary.members_tagged += 1
        summary.members_modified += 1
    return summary
