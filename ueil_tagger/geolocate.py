from diskcache import Cache
from geopy.geocoders import Nominatim

import ueil_tagger
from ueil_tagger import STATE_DIR_PATH
from ueil_tagger.types import Coords


def coords_for_address(address: str) -> Coords:
    cache = Cache(STATE_DIR_PATH)
    if address in cache:
        return Coords(*cache[address])

    geolocator = Nominatim(user_agent=ueil_tagger.APP_NAME)
    location = geolocator.geocode(address, timeout=30)
    coords = Coords(location.latitude, location.longitude)

    cache[address] = (coords.lat, coords.long)
    cache.close()
    return coords
