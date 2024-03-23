import json

from pathlib import Path

from runners.cli import CliRunner
from config import paths

def all(config_dirs: list[Path]=paths.engine_config_dirs) -> dict[str, CliRunner]:
    config_files=[]
    for dir in config_dirs:
        config_files.extend(dir.glob('*.json'))

    result: dict = {}
    for file_path in config_files:
        with open(file_path, "r") as file:
            config=json.load(file)

            if config["connection"] == "CLI":
                result[config["name"]] = CliRunner(config)

    return result
