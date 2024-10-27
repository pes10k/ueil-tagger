import logging
from typing import Optional

from diskcache import Cache
from geopy.geocoders import Nominatim

import ueil_tagger
from ueil_tagger import STATE_DIR_PATH
from ueil_tagger.types import Coords


def coords_for_address(address: str) -> Optional[Coords]:
    logging.debug(" - About to geocode '%s'", address)
    cache = Cache(STATE_DIR_PATH)
    if address in cache:
        cached_coords = Coords(*cache[address])
        logging.debug(" * Geocode cache '%s' to (lat=%s, long=%s)",
                      address, cached_coords.lat, cached_coords.long)
        return cached_coords

    geolocator = Nominatim(user_agent=ueil_tagger.APP_NAME)
    location = geolocator.geocode(address, timeout=30)
    if not location:
        logging.error(" ! Unable to geocode '%s'", address)
        return None
    logging.debug(" * Successfully geocoded '%s' to (lat=%s, long=%s)",
                  address, location.latitude, location.longitude)
    coords = Coords(location.latitude, location.longitude)

    cache[address] = (coords.lat, coords.long)
    cache.close()
    return coords
