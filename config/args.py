import argparse
import json
import sys

from pathlib import Path
from config.paths import BasePaths

## Command line arguments
parser = argparse.ArgumentParser()

# ip address
parser.add_argument(
    '--host', 
    default="0.0.0.0",                      
    help="ip address/domain for the app to listen on",
)

# port
parser.add_argument(
    '--port', 
    default=8080, 
    type=int,            
    help="port for the app to listen on", 
)

# develop mode
parser.add_argument(
    '--dev',    
    default=False,     
    action="store_true", 
    help="reload app source code when edits are to it are saved", 
)

# file location to load/store the app configuration 
parser.add_argument(
    '--config', 
    default=BasePaths.config_file,
    help="file location to load/store app configuration", 
)

# base directory to place generated images
parser.add_argument(
    '--output_dir', 
    default=BasePaths.output_dir,
    help="output folder to put generated images", 
)

# whether to follow symbolic links when searching subdirectories
parser.add_argument(
    '--followlinks',
    default=True,
    action="store_true", 
    help="whether to follow links when searching subdirectories"
)

args = parser.parse_args()

## Do any BasePath adjustments from command line settings
BasePaths.output_dir = Path(args.output_dir)
BasePaths.config_file = Path(args.config)

## Configuration file
DEFAULT_CONFIG = {
    "version:": 1,
    "generators": []
}

# Create config file if it does not exist
if not Path(BasePaths.config_file).exists():
    try:
        Path.mkdir(BasePaths.config_file.parent,  parents=True, exist_ok=True)
        with open(BasePaths.config_file, "w", encoding='utf-8') as config_file:
            json.dump(DEFAULT_CONFIG, config_file)
    except OSError:
        print(f"Could not create config file at: {args.config}")
        sys.exit()


# Load config
config = {}
with open(BasePaths.config_file, "r") as config_file:
    try:
        with open(BasePaths.config_file, "r", encoding='utf-8') as config_file:
            config = json.load(config_file)
    except OSError:            
        print(f"Could not read config file at: {args}")
        sys.exit()


