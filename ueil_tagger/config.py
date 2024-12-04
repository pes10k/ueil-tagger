from __future__ import annotations

import functools
from datetime import datetime
import logging
import tomllib
from typing import cast, Optional, TYPE_CHECKING

from ueil_tagger import ROOT_DIR_PATH, STATE_DIR_PATH

if TYPE_CHECKING:
    from ueil_tagger.types import ConfigSettings


@functools.cache
def get_config() -> ConfigSettings:
    config_file_path = ROOT_DIR_PATH / "config.toml"
    if not config_file_path.is_file():
        raise ValueError(
            f"No config file found at {str(config_file_path.absolute())}")
    config = cast("ConfigSettings",
                  tomllib.loads(config_file_path.read_text()))
    return config


def get_api_key() -> str:
    config = get_config()
    return cast(str, config["action-network-api-key"])


def get_min_zip_sqft() -> float:
    config = get_config()
    return cast(float, config["min-zip-sqft"])


def get_last_run() -> Optional[datetime]:
    last_run_path = STATE_DIR_PATH / "last_run.txt"
    if not last_run_path.is_file():
        return None
    last_run_text = last_run_path.read_text()
    try:
        last_run_date = datetime.fromisoformat(last_run_text)
        return last_run_date
    except ValueError:
        last_run_path_str = str(last_run_path.absolute())
        logging.error("Invalid date format stored in '%s'", last_run_path_str)
        return None


def set_last_run(last_run_date: datetime) -> None:
    last_run_path = STATE_DIR_PATH / "last_run.txt"
    last_run_path.write_text(last_run_date.isoformat())
