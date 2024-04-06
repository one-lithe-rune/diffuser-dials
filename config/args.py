import argparse

from platformdirs import user_config_path, user_pictures_dir, user_documents_path
from config.paths import AppPaths

APP_TITLE = "diffuser dials"
APP_NAME = APP_TITLE.lower().replace(" ", "-")

# --- Command line arguments ---
parser = argparse.ArgumentParser()

# ip address or hostname
parser.add_argument(
    "--host",
    default="localhost",
    help="ip address/domain for the app to listen on",
)

# port
parser.add_argument(
    "--port",
    default=8098,
    type=int,
    help="port for the app to listen on",
)

# file location to load/store the app configuration
parser.add_argument(
    "--config_dir",
    default=user_config_path(APP_NAME),
    help="file location to load/store app configuration",
)

# whether to follow symbolic links when searching subdirectories
parser.add_argument(
    "--followlinks",
    default=True,
    action="store_true",
    help="whether to follow symbolic links when searching subdirectories",
)

# base directory to place generated images
parser.add_argument(
    "--output_dir",
    default=user_pictures_dir(),
    help="output folder to put generated images",
)

# base directory for retrieving models
parser.add_argument(
    "--models",
    default=user_documents_path() / "models",
    help="parent folder of subfolders for checkpoints, vaes, loras, and embeddings",
)

parser.add_argument(
    "--checkpoints",
    help="overrides folder for checkpoints if not under the models folder",
)

parser.add_argument(
    "--vaes", help="overrides folder for vaes if not under the models folder"
)

parser.add_argument(
    "--loras", help="overrides folder for loras if not under the models folder"
)

parser.add_argument(
    "--embeddings", help="overrides folder for loras if not under the models folder"
)

args = parser.parse_args()
paths = AppPaths(args)
