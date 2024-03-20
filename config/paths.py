import sys

from pathlib import Path
from platformdirs import user_config_path, user_pictures_dir
from datetime import datetime

## Application paths

APP_TITLE = "diffuser dials"
APP_NAME = APP_TITLE.lower().replace(" ", "-")

class BasePaths:
    # works for both pyinstaller packaged and not pysintaller packaged
    # make sure you change the .parent clause if you move this file within
    # the project structure
    resources: Path = Path(getattr(sys, "_MEIPASS", Path(__file__).absolute().parent.parent))
    css: Path = resources / "css"
    js: Path = resources / "js"
    images: Path = resources / "images"
    stylesheet: Path = css / "styles.css"
    container_stylesheet: Path = css / "container_styles.css"
    workarounds: Path = js / "workarounds.js"
    config_file: Path = Path(user_config_path(APP_NAME)) / "config.json"
    output_dir: Path = Path(user_pictures_dir())

def dated_output_dir():
    return BasePaths.output_dir / datetime.now().strftime("%Y%m%d") 