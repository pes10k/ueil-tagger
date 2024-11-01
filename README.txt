usage: UE IL Member Tagger [-h] [--version] [--api-key API_KEY]
                           [--min-sqft MIN_SQFT] [--since SINCE]
                           [--uuid [UUID ...]] [--verbose]

Updates the Ward tags in the UE IL ActionNetwork database.
Decides which ward(s) to tag the member with as follows:

  - If the member explicitly provided their ward #, and it
    looks valid (e.g., an integer between 1 and 50), we
    assume thats correct and use that value. Otherwise...
  - If the member provided something that looks like a
    complete street address, try to geocode that address
    using the www.openstreetmap.org API, and see if it falls
    with in a Chicago Ward. Otherwise...
  - If the member provided a zipcode, see if that zipcode
    overlaps with any Chicago Wards (based on data from
    www.chicagocityscape.com), and if so, tag the member
    with all possible wards.

If none of the above strategies work, the member is not tagged.

options:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  --api-key API_KEY    API key for the UE IL database, from
                       https://actionnetwork.org/groups/urban-
                       environmentalists-il/apis. (default: -----)
  --min-sqft MIN_SQFT  The minimum number of square feet that a zipcode must
                       overlap with a ward's area in order for members in that
                       zipcode to be tagged with the ward. (default: 10000)
  --since SINCE        If provided, only modify members who's information has
                       changed since the given date (date should be provided
                       in ISO 8601 format). If a timezone isn't included,
                       assumes UTC. (default: -----)
  --uuid [UUID ...]    If provided, then only the specified person records are
                       loaded and modified. In this case, the --since argument
                       is ignored. (default: None)
  --verbose, -v        If provided once, then info messages are logged. If
                       provided two or more times, then log debug messages (If
                       not provided, then only error messages are logged).
                       (default: 0)
