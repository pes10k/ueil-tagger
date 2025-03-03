#!/usr/bin/env python3

import argparse
import datetime
import logging
import sys

import ueil_tagger
import ueil_tagger.cache
import ueil_tagger.client
import ueil_tagger.config
import ueil_tagger.members
import ueil_tagger.types


LAST_RUN_DATETIME = ueil_tagger.config.get_last_run()

PARSER = argparse.ArgumentParser(
    prog=ueil_tagger.APP_NAME,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Updates the Ward tags in the UE IL ActionNetwork database.\n"
                "Decides which ward(s) to tag the member with as follows:\n\n"
                "  - If the member explicitly provided their ward #, and it\n"
                "    looks valid (e.g., an integer between 1 and 50), we\n"
                "    assume thats correct and use that value. Otherwise...\n"
                "  - If the member provided something that looks like a\n"
                "    complete street address, try to geocode that address\n"
                "    using the www.openstreetmap.org API, and see if it\n"
                "    falls with in a Chicago Ward. Otherwise...\n"
                "  - If the member provided a zipcode, see if that zipcode\n"
                "    overlaps with any Chicago Wards (based on data from\n"
                "    www.chicagocityscape.com), and if so, tag the member\n"
                "    with all possible wards.\n"
                "\n"
                "If none of the above strategies work, the member is not "
                "tagged.")
PARSER.add_argument(
    "--version",
    action="version",
    version="%(prog)s " + ueil_tagger.__version__)
PARSER.add_argument(
    "--api-key",
    default=ueil_tagger.config.get_api_key(),
    help="API key for the UE IL database, from "
         "https://actionnetwork.org/groups/urban-environmentalists-il/apis. "
         "(default: %(default)s)")
PARSER.add_argument(
    "--min-sqft",
    default=ueil_tagger.config.get_min_zip_sqft(),
    type=float,
    help="The minimum number of square feet that a zipcode must overlap with "
         "a ward's area in order for members in that zipcode to be tagged "
         "the ward. (default: %(default)s)")
PARSER.add_argument(
    "--since",
    default=LAST_RUN_DATETIME.isoformat() if LAST_RUN_DATETIME else None,
    help="If provided, only modify members who's information has changed "
         "since the given date (date should be provided in ISO 8601 format). "
         "If a timezone isn't included, assumes UTC. (default: %(default)s)")
PARSER.add_argument(
    "--batch",
    help="If provided, keep track of person uuids that have been updated "
         "within a 'batch', to prevent repeatedly updating the same records.",
    default=False,
    action="store_true"
)
PARSER.add_argument(
    "--clear-batch-cache",
    help="If provided, reset the existing batch cache before updating any "
         "member tags.",
    default=False,
    action="store_true"
)
PARSER.add_argument(
    "--uuid",
    nargs="*",
    help="If provided, then only the specified person records are loaded and "
         "modified. In this case, the --since argument is ignored. "
         "(default: %(default)s)")
PARSER.add_argument(
    "--dry-run",
    help="Don't make any changes to the database, just print information as "
         "if changes were being made. What messages are printed is controlled "
         "by --verbose.",
    action="store_true",
    default=False
)
PARSER.add_argument(
    "--verbose", "-v",
    action="count",
    default=0,
    help="If provided once, then print info messages. If provided two or "
         "more times, then also print debug messages (If not provided, then "
         "only error messages are printed). (default: %(default)s)")
ARGS = PARSER.parse_args()

if ARGS.verbose == 0:
    logging.basicConfig(level=logging.ERROR)
elif ARGS.verbose == 1:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

if not ARGS.api_key:
    logging.error("Must provide an API key, either with --api-key or "
                  "in 'config.toml'")
    sys.exit(1)

CLIENT = ueil_tagger.client.Client(ARGS.api_key, ARGS.dry_run)
UPDATED_SINCE = None
SUMMARY = None

if ARGS.clear_batch_cache:
    logging.info("Clearing batch cache")
    CACHE = ueil_tagger.cache.TaggerCache()
    CACHE.clear_member_uuid_cache()

if ARGS.uuid:
    for person_uuid in ARGS.uuid:
        SUMMARY = ueil_tagger.members.set_ward_tags_for_member_uuid(
                CLIENT, person_uuid, ARGS.min_sqft, SUMMARY)
        if SUMMARY.encountered_error():
            sys.exit(1)
else:
    if ARGS.since:
        try:
            UPDATED_SINCE = datetime.datetime.fromisoformat(ARGS.since)
            # If a timezone wasn't included, use the local system timezone.
            if not UPDATED_SINCE.tzname():
                local_tz = datetime.datetime.now().astimezone().tzinfo
                UPDATED_SINCE = UPDATED_SINCE.replace(tzinfo=local_tz)
                logging.info("Date for --since did not include a timezone; "
                             "Using the system timezone '%s'.",
                             UPDATED_SINCE.tzname())
        except ValueError:
            logging.error("Invalid date for --since argument: '%s'. Must",
                          ARGS.since)
            sys.exit(1)

    SUMMARY = ueil_tagger.members.set_ward_tags_for_all_members_since(
        CLIENT, ARGS.min_sqft, ARGS.batch, UPDATED_SINCE)
    if not ARGS.dry_run:
        NOW_UTC_TIME = datetime.datetime.now(datetime.timezone.utc)
        ueil_tagger.config.set_last_run(NOW_UTC_TIME)

assert SUMMARY
print(SUMMARY.to_json())
sys.exit(0)
