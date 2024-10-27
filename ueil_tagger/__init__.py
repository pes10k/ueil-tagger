__author__ = "Peter Snyder"
__version__ = "0.1"


from pathlib import Path


APP_NAME = "UE IL Member Tagger"
ROOT_DIR_PATH = Path(__file__).parent.parent.absolute()
DATA_DIR_PATH = ROOT_DIR_PATH / "data"
STATE_DIR_PATH = ROOT_DIR_PATH / "app_state"
