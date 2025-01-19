import argparse
from pathlib import Path

from kanaplex.config import parse_config, ConfigError, CFG_FILENAME
from kanaplex.symlink import create_symlink_for_missing_episodes

VERSION = "0.3.1"

def main():
    parser = argparse.ArgumentParser(description=f"Symlink downloaded episodes based on '{CFG_FILENAME}' config file.")
    parser.add_argument("directory", help="Directory where the torrent has been downloaded.")

    args = parser.parse_args()
    directory = Path(args.directory)

    if not directory.exists() or not directory.is_dir():
        print(f"Error: {directory} is not a valid directory.")
        return

    try:
        config = parse_config(directory)
        name = config["name"]
        print(f"[kanaplex v{VERSION}] {name}")
        create_symlink_for_missing_episodes(directory, config)
    except ConfigError as e:
        print(f"Config Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
