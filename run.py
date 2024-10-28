#!/usr/bin/env python3

import argparse
import datetime
import logging
import sys

import ueil_tagger
import ueil_tagger.client
import ueil_tagger.config
import ueil_tagger.members
import ueil_tagger.types


LAST_RUN_DATETIME = ueil_tagger.config.get_last_run()

PARSER = argparse.ArgumentParser(
    prog=ueil_tagger.APP_NAME,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Updates the Ward tags in the UE IL ActionNetwork database.")
PARSER.add_argument(
    "--version",
    action="version",
    version="%(prog)s " + ueil_tagger.__version__)
PARSER.add_argument(
    "--api-key",
    default=ueil_tagger.config.get_api_key(),
    help="API key for the UE IL database, from "
         "https://actionnetwork.org/groups/urban-environmentalists-il/apis.")
PARSER.add_argument(
    "--min-sqft",
    default=ueil_tagger.config.get_min_zip_sqft(),
    type=float,
    help="The minimum number of square feet that a zipcode must overlap with "
         "a ward's area in order for members in that zipcode to be tagged with "
         "the ward.")
PARSER.add_argument(
    "--since",
    default=LAST_RUN_DATETIME.isoformat() if LAST_RUN_DATETIME else None,
    help="If provided, only modify members who's information has changed since "
         "the given date (date should be provided in ISO 8601 format). If "
         "a timezone isn't included, assumes UTC.")
PARSER.add_argument(
    "--uuid",
    nargs="*",
    help="If provided, then only the specified person records are loaded and "
         "modified. In this case, the --since argument is ignored.")
PARSER.add_argument(
    "--verbose", "-v",
    action="count",
    default=0,
    help="If provided once, then info messages are logged. If provided two or "
         "more times, then log debug messages (If not provided, then only "
         "error messages are logged).")
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

CLIENT = ueil_tagger.client.Client(ARGS.api_key)
UPDATED_SINCE = None
SUMMARY = None

if ARGS.uuid:
    SUMMARY = ueil_tagger.types.TaggingsSummary()
    for person_uuid in ARGS.uuid:
        is_success, _ = ueil_tagger.members.set_ward_tags_for_member_uuid(
                CLIENT, person_uuid, ARGS.min_sqft, SUMMARY)
        if not is_success:
            sys.exit(1)

else:
    if ARGS.since:
        try:
            UPDATED_SINCE = datetime.datetime.fromisoformat(ARGS.since)
            # If a timezone wasn't included, use the local system timezone.
            if not UPDATED_SINCE.tzname():
                local_tz = datetime.datetime.now().astimezone().tzinfo
                UPDATED_SINCE = UPDATED_SINCE.replace(tzinfo=local_tz)
                logging.info("Date for --since did not include a timezone; Using "
                            "the system timezone '%s'.", UPDATED_SINCE.tzname())
        except ValueError:
            logging.error("Invalid date for --since argument: '%s'. Must", ARGS.since)
            sys.exit(1)

    SUMMARY = ueil_tagger.members.set_ward_tags_for_all_members_since(
        CLIENT, ARGS.min_sqft, UPDATED_SINCE)
    ueil_tagger.config.set_last_run(datetime.datetime.now(datetime.timezone.utc))

assert SUMMARY
print(SUMMARY.to_json())
sys.exit(0)
