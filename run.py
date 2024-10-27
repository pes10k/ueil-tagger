#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import sys

import ueil_tagger
import ueil_tagger.client
import ueil_tagger.config
import ueil_tagger.members


last_run_datetime = ueil_tagger.config.get_last_run()

PARSER = argparse.ArgumentParser(
    prog=ueil_tagger.APP_NAME,
    description="Updates the Ward tags in the UE IL ActionNetwork database.")
PARSER.add_argument(
    "--version",
    action="version",
    version="%(prog)s " + ueil_tagger.__version__)
PARSER.add_argument(
    "--api-key",
    default=ueil_tagger.config.get_api_key(),
    required=True,
    help="API key for the UE IL database, from "
         "https://actionnetwork.org/groups/urban-environmentalists-il/apis.")
PARSER.add_argument(
    "--min-sqft",
    default=ueil_tagger.config.get_min_zip_sqft(),
    type=float,
    required=True,
    help="The minimum number of square feet that a zipcode must overlap with "
         "a ward's area in order for members in that zipcode to be tagged with "
         "the ward.")
PARSER.add_argument(
    "--since",
    default=last_run_datetime.isoformat() if last_run_datetime else None,
    help="If provided, only modify members who's information has changed since "
         "the given date (date should be provided in ISO format).")
PARSER.add_argument(
    "--verbose", "-v",
    action="count",
    default=0,
    help="If provided once, then info messages are logged. If provided two or "
         "more times, then log debug messages (If not provided, then only "
         "error messages are logged).")
ARGS = PARSER.parse_args()

UPDATED_SINCE = None
if ARGS.since:
    try:
        UPDATED_SINCE = datetime.fromisoformat(ARGS.since)
    except ValueError:
        logging.error("Invalid date for --since argument: %s", UPDATED_SINCE)
        sys.exit(1)

if ARGS.verbose == 0:
    logging.basicConfig(level=logging.ERROR)
elif ARGS.verbose == 1:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

CLIENT = ueil_tagger.client.Client(ARGS.api_key)

SUMMARY = ueil_tagger.members.set_ward_tags_for_all_members_since(
    CLIENT, ARGS.min_sqft, UPDATED_SINCE)
ueil_tagger.config.set_last_run(datetime.now())
print(SUMMARY.to_json())
sys.exit(0)
