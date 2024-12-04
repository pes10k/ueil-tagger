from __future__ import annotations

from datetime import datetime
import json
import logging
from typing import Any, cast, Optional, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from ueil_tagger.types import Uuid, WebAPIRecord


PEOPLE_ENDPOINT = "https://actionnetwork.org/api/v2/people"
TAGS_ENDPOINT = "https://actionnetwork.org/api/v2/tags"


class Client:
    api_key: str
    read_only: bool

    def __init__(self, api_key: str, dry_run: bool = False) -> None:
        self.api_key = api_key
        self.read_only = dry_run

    def __delete(self, url: str, background: bool = True) -> bool:
        headers = {
            "api-key": self.api_key
        }
        params = {}
        if background:
            params["background_request"] = "true"
        logging.debug("(DELETE) %s params=(%s)", url, json.dumps(params))
        if self.read_only:
            return True
        rs = requests.delete(url, headers=headers, params=params, timeout=10)
        logging.debug("...%s: %s bytes", rs.status_code, len(rs.content))
        return rs.ok

    def __post(self, url: str, data: Optional[Any],
               background: bool = True) -> bool:
        headers = {
            "Content-Type": "application/json",
            "OSDI-API-Token": self.api_key
        }
        params = {}
        if background:
            params["background_request"] = "true"
        logging.debug("(POST) %s params=(%s) data=(%s)",
                      url, json.dumps(params), json.dumps(data))
        if self.read_only:
            return True
        rs = requests.post(url, json=data, headers=headers, params=params,
                           timeout=10)
        logging.debug("...%s: %s bytes", rs.status_code, len(rs.content))
        if not rs.ok:
            logging.error("Unexpected response from the server:\n%s",
                          rs.text)
        return rs.ok

    def __get(self, url: str,
              params: Optional[dict[str, str]] = None) -> WebAPIRecord:
        if not params:
            params = {}
        headers = {
            "Content-Type": "application/json",
            "OSDI-API-Token": self.api_key
        }
        logging.debug("(GET) %s params=(%s)", url, json.dumps(params))
        rs = requests.get(url, params=params, headers=headers, timeout=10)
        logging.debug("...%s: %s bytes", rs.status_code, len(rs.content))
        return cast("WebAPIRecord", rs.json())

    def get_tags(self, page: int = 1) -> WebAPIRecord:
        params = {
            "page": str(page)
        }
        return self.__get(TAGS_ENDPOINT, params)

    def get_people(self, page: int = 1,
                   modified_since: Optional[datetime] = None) -> WebAPIRecord:
        params = {
            "page": str(page)
        }
        if modified_since is not None:
            date_filter = f"modified_date gt '{modified_since.isoformat()}'"
            params["filter"] = date_filter
        return self.__get(PEOPLE_ENDPOINT, params)

    def get_person(self, person_uuid: Uuid) -> WebAPIRecord:
        url = f"{PEOPLE_ENDPOINT}/{person_uuid}"
        return self.__get(url, {})

    def set_tagging_for_person(self, tag_uuid: Uuid, person_uuid: Uuid,
                               background: bool = True) -> bool:
        person_url = f"{PEOPLE_ENDPOINT}/{person_uuid}"
        url = f"{TAGS_ENDPOINT}/{tag_uuid}/taggings"
        data = {
            "_links": {
                "osdi:person": {
                    "href": person_url
                }
            }
        }
        return self.__post(url, data, background=background)

    def get_taggings_for_person(self, person_uuid: Uuid,
                                page: int = 1) -> list[Uuid]:
        url = f"{PEOPLE_ENDPOINT}/{person_uuid}/taggings"
        params = {
            "page": str(page)
        }
        results = self.__get(url, params)
        tag_uuids = []
        for tag in results["_embedded"]["osdi:taggings"]:
            tag_href = tag["_links"]["osdi:tag"]["href"]
            tag_uuid = tag_href.split("/")[-1]
            tag_uuids.append(tag_uuid)
        return tag_uuids

    def delete_tagging_for_person(self, tag_uuid: Uuid, person_uuid: Uuid,
                                  background: bool = True) -> bool:
        url = f"{TAGS_ENDPOINT}/{tag_uuid}/taggings/{person_uuid}"
        return self.__delete(url, background=background)
