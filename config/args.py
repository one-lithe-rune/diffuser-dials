import argparse
import json

from platformdirs import user_config_path, user_pictures_dir, user_documents_path
from config.paths import AppPaths
from pathlib import Path

APP_TITLE = "diffuser dials"
APP_NAME = APP_TITLE.lower().replace(" ", "-")

print(f"\nStarting {APP_TITLE}...")

# --- Defaults for the arguments ---

defaults = {
    "host": "localhost",
    "port": 8098,
    "followlinks": True,
    "output_dir": str(user_pictures_dir()),
    "models": str(user_documents_path() / "models"),
    "checkpoints": None,
    "vaes": None,
    "loras": None,
    "embeddings": None,
}

# override the defaults with the ones in the config file if it exists
if (user_config_path(APP_NAME) / "config.json").exists():
    with open(user_config_path(APP_NAME) / "config.json") as config:
        try:
            defaults = json.load(config)
        except json.JSONDecodeError:
            print("Could not parse config file, skipping")

# --- Command line arguments ---
parser = argparse.ArgumentParser()

# ip address or hostname
parser.add_argument(
    "--host",
    default=defaults["host"],
    help="ip address/domain for the app to listen on",
)

# port
parser.add_argument(
    "--port",
    default=defaults["port"],
    type=int,
    help="port for the app to listen on",
)

# file location to load/store the app configuration
parser.add_argument(
    "--config_dir",
    default=str(user_config_path(APP_NAME)),
    help="file location to load/store app configuration",
)

# whether to follow symbolic links when searching subdirectories
parser.add_argument(
    "--followlinks",
    default=defaults["followlinks"],
    action="store_true",
    help="whether to follow symbolic links when searching subdirectories",
)

# whether to update the saved config based on argument settings
parser.add_argument(
    "--update_config",
    default=False,
    action="store_false",
    help="whether to update the saved config to these command line settings",
)

# base directory to place generated images
parser.add_argument(
    "--output_dir",
    default=defaults["output_dir"],
    help="output folder to put generated images",
)

# base directory for retrieving models
parser.add_argument(
    "--models",
    default=defaults["models"],
    help="parent folder of subfolders for checkpoints, vaes, loras, and embeddings",
)

parser.add_argument(
    "--checkpoints",
    default=defaults["checkpoints"],
    help="overrides folder for checkpoints if not under the models folder",
)

parser.add_argument(
    "--vaes",
    default=defaults["vaes"],
    help="overrides folder for vaes if not under the models folder",
)

parser.add_argument(
    "--loras",
    default=defaults["loras"],
    help="overrides folder for loras if not under the models folder",
)

parser.add_argument(
    "--embeddings",
    default=defaults["embeddings"],
    help="overrides folder for loras if not under the models folder",
)

args = parser.parse_args()
paths = AppPaths(args)

print("\nUsing configuration settings:")
print(json.dumps(vars(args), indent=4))
print("Directory paths for checkpoints, vaes, loras or embeddings, are")
print("taken to be subdirectories of the models directory when set to null.\n")

# write the command line args to the the config file if we don't have one or
# we were asked to update it
if args.update_config or not (Path(args.config_dir) / "config.json").exists():
    Path(args.config_dir).mkdir(exist_ok=True)
    with open(Path(args.config_dir) / "config.json", "w") as config:
        json.dump(vars(args), config, indent=4)

    print(f"Config file written to: {Path(args.config_dir) / 'config.json'}")
