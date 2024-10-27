```
usage: UE IL Member Tagger [-h] [--version] [--api-key API_KEY]
                           [--min-sqft MIN_SQFT] [--since SINCE] [--verbose]

Updates the Ward tags in the UE IL ActionNetwork database.

options:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  --api-key API_KEY    API key for the UE IL database, from
                       https://actionnetwork.org/groups/urban-
                       environmentalists-il/apis. (default: --)
  --min-sqft MIN_SQFT  The minimum number of square feet that a zipcode must
                       overlap with a ward's area in order for members in that
                       zipcode to be tagged with the ward. (default: 10000)
  --since SINCE        If provided, only modify members who's information has
                       changed since the given date (date should be provided
                       in ISO format). (default: --)
  --verbose, -v        If provided once, then info messages are logged. If
                       provided two or more times, then log debug messages (If
                       not provided, then only error messages are logged).
                       (default: 0)
```