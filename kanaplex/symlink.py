import os
from pathlib import Path

# TODO: implement preferred_contains:
#       if there are 2 files for the same episode, prefer one that contains
#       the string 'preferred_contains'

# TODO: implement manual single episode symlink

def parse_episode_id(episode_path: Path) -> str:
    """
    Parses an episode ID from a given file name and returns it in the format 'SXXEYY'.

    If the season is not explicitly provided, season 1 is assumed (S01).

    Parameters:
        episode_path (Path): The path to the file whose name contains episode information.

    Returns:
        str: The parsed episode ID in the format 'SXXEYY', or an empty string if no valid episode number is found.
    """
    # Split the filename into parts based on spaces, dots, or dashes
    parts = episode_path.stem.replace('.', ' ').replace('-', ' ').split()

    season = 1
    episode = None

    for i, part in enumerate(parts):
        part_lower = part.lower()

        # Check for "SXXEYY" pattern
        if "s" in part_lower and "e" in part_lower:
            if (version_index := part_lower.find('v')) >= 0:
                part_lower = part_lower[:version_index]
            try:
                s_index = part_lower.index("s") + 1
                e_index = part_lower.index("e") + 1
                season = int(part_lower[s_index:e_index - 1])
                episode = int(part_lower[e_index:])
                break
            except ValueError:
                continue

        # Check for "SXX" or "EYY" separately
        elif part_lower.startswith("s") and part_lower[1:].isdigit():
            season = int(part_lower[1:])
        elif part_lower.startswith("e") and part_lower[1:].isdigit():
            episode = int(part_lower[1:])

        # Check for standalone episode number as last part
        elif part.isdigit() and i == len(parts) - 1:
            episode = int(part)

    if episode is not None:
        return f"S{season:02d}E{episode:02d}"

    return ""

def find_existing_episodes(dest_dir: Path):
    """
    Identify episodes already present in the destination directory.

    :param destination_dir: Path to the destination directory.
    :return: A set of episode identifiers (e.g., 'S01E01').
    """
    existing_episodes = set()
    if not dest_dir.exists():
        return existing_episodes  # No files in the destination yet.

    for file in dest_dir.iterdir():
        if file.is_file():
            if episode_id := parse_episode_id(file):
                existing_episodes.add(episode_id)

    print(f"  - Found {len(existing_episodes)} episode(s) in Plex.")
    return existing_episodes


def find_available_episodes(source_dir: Path):
    """
    Identify episodes available in the source directory.

    :param source_dir: Path to the source directory (torrent folder).
    :return: A dictionary mapping episode IDs to file paths.
    """
    episodes = {}
    for file in source_dir.iterdir():
        if file.is_file():
            if episode_id := parse_episode_id(file):
                episodes[episode_id] = file

    print(f"  - Found {len(episodes)} episode(s) in the torrent folder.")
    return episodes


def create_symlink_for_missing_episodes(source_dir: Path, config: dict):
    """
    Create symlinks for missing episodes based on the source and destination directories.

    :param source_dir: Path to the source directory (torrent folder).
    :param config: Configuration dictionary containing destination and name.
    """
    name = config["name"]
    dest_path = Path(config["destination"])

    dest_path.mkdir(parents=True, exist_ok=True)

    existing_episodes = find_existing_episodes(dest_path)
    available_episodes = find_available_episodes(source_dir)

    missing_episodes = {
        episode_id: file
        for episode_id, file in available_episodes.items()
        if episode_id not in existing_episodes
    }

    if not missing_episodes:
        print("No new episodes to symlink.")
        return

    print(f"  - Found {len(missing_episodes)} episode(s) to symlink:")

    for episode_id, source_file in missing_episodes.items():
        dest_file = dest_path / f"{name} - {episode_id}"
        dest_file = dest_file.with_suffix(source_file.suffix)

        try:
            os.symlink(source_file, dest_file)
            print(f"    * {source_file}")
            print(f"      -> {dest_file}")
        except FileExistsError:
            print(f"    * Error: symlink already exists: {dest_file}")
        except Exception as e:
            print(f"    * Error creating symlink for {source_file}: {e}")
