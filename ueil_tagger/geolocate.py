import logging
from typing import Optional

from geopy.geocoders import Nominatim

import ueil_tagger
from ueil_tagger.cache import TaggerCache
from ueil_tagger.types import Coords


def coords_for_address(address: str) -> Optional[Coords]:
    logging.debug(" - About to geocode '%s'", address)
    cache = TaggerCache()
    cache_result = cache.get_for_address(address)
    if cache_result:
        cached_coords = Coords(*cache_result)
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

    cache.set_for_address(address, (coords.lat, coords.long))
    return coords
