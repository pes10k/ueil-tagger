from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from diskcache import Cache

from ueil_tagger import STATE_DIR_PATH


if TYPE_CHECKING:
    from ueil_tagger.types import StreetAddress, LatLong, Uuid


class TaggerCache:
    ADDRESS_CACHE_KEY = "addresses"
    BATCH_CACHE_KEY = "batch"

    def set_for_address(self, address: StreetAddress,
                        value: LatLong) -> None:
        cache = Cache(STATE_DIR_PATH / self.ADDRESS_CACHE_KEY)
        cache.set(address, value)
        cache.close()

    def get_for_address(self, address: StreetAddress) -> Optional[LatLong]:
        cache = Cache(STATE_DIR_PATH / self.ADDRESS_CACHE_KEY)
        if address in cache:
            return cast("LatLong", cache[address])
        return None

    def set_member_uuid(self, member_uuid: Uuid) -> None:
        cache = Cache(STATE_DIR_PATH / self.BATCH_CACHE_KEY)
        cache.set(member_uuid, True)
        cache.close()

    def check_member_uuid(self, member_uuid: Uuid) -> bool:
        cache = Cache(STATE_DIR_PATH / self.BATCH_CACHE_KEY)
        if member_uuid in cache:
            return True
        return False

    def clear_member_uuid_cache(self) -> None:
        cache = Cache(STATE_DIR_PATH / self.BATCH_CACHE_KEY)
        cache.clear()
