import configparser
from pathlib import Path


CFG_FILENAME = ".kanaplex"


class ConfigError(Exception):
    pass

def parse_config(directory: Path):
    """
    Parse the CFG_FILENAME file in the given directory.

    :param directory: Path to the directory containing the CFG_FILENAME file.
    :return: A dictionary with the parsed settings.
    """
    config_path = Path(directory, CFG_FILENAME)

    if not config_path.exists():
        raise ConfigError(f"No {CFG_FILENAME} file found in {directory}")

    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        name = config["settings"]["name"]
        destination = config["settings"]["destination"]
    except KeyError as e:
        raise ConfigError(f"Missing required config key '{e}'")

    return {
        "name": name,
        "destination": destination,
    }
