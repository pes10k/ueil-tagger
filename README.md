```
usage: UE IL Member Tagger [-h] [--version] [--api-key API_KEY]
                           [--min-sqft MIN_SQFT] [--since SINCE]
                           [--uuid [UUID ...]] [--verbose]

Updates the Ward tags in the UE IL ActionNetwork database.

options:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  --api-key API_KEY    API key for the UE IL database, from
                       https://actionnetwork.org/groups/urban-
                       environmentalists-il/apis. (default:
                       df93cf2bccc7ae50bdd51496a7fabace)
  --min-sqft MIN_SQFT  The minimum number of square feet that a zipcode must
                       overlap with a ward's area in order for members in that
                       zipcode to be tagged with the ward. (default: 10000)
  --since SINCE        If provided, only modify members who's information has
                       changed since the given date (date should be provided
                       in ISO 8601 format). If a timezone isn't included,
                       assumes UTC. (default:
                       2024-10-28T04:42:16.519470+00:00)
  --uuid [UUID ...]    If provided, then only the specified person records are
                       loaded and modified. In this case, the --since argument
                       is ignored. (default: None)
  --verbose, -v        If provided once, then info messages are logged. If
                       provided two or more times, then log debug messages (If
                       not provided, then only error messages are logged).
                       (default: 0)
```
