import sys

from pathlib import Path
from typing import Literal


class AppPaths:
    """Class exposing the file system paths to use throughout the application"""

    def __init__(self, app_arguments):
        # works for both pyinstaller packaged and not pysintaller packaged
        # make sure you change the .parent clause if you move this file within
        # the project structure
        self.resources: Path = Path(
            getattr(sys, "_MEIPASS", Path(__file__).absolute().parent.parent)
        )
        self.css: Path = self.resources / "css"
        self.js: Path = self.resources / "js"
        self.images: Path = self.resources / "images"
        self.stylesheet: Path = self.css / "styles.css"
        self.container_stylesheet: Path = self.css / "container_styles.css"
        self.workarounds: Path = self.js / "workarounds.js"
        self.config_dir: Path = Path(app_arguments.config_dir)
        self.output_dir: Path = [
            dir for dir in app_arguments.output_dir if Path(dir).is_dir()
        ]
        self.engine_config_dirs: list[Path] = [
            self.config_dir / "engines",
            self.resources / "config" / "engines",
        ]
        self.models: Path = Path(app_arguments.models)
        self.checkpoints: Path = (
            Path(app_arguments.checkpoints)
            if app_arguments.checkpoints
            else self.models / "checkpoint"
        )
        self.vaes: Path = (
            Path(app_arguments.vaes) if app_arguments.vaes else self.models / "vae"
        )
        self.loras: Path = (
            Path(app_arguments.loras) if app_arguments.loras else self.models / "lora"
        )
        self.embeddings: Path = (
            Path(app_arguments.embeddings)
            if app_arguments.embeddings
            else self.models / "embedding"
        )

    def for_placeholder(
        self,
        placeholder: Literal["$checkpoints", "$vaes", "$loras", "$embeddings"],
    ):
        """Return the path corresponding to a placeholder string"""
        match placeholder:
            case "$checkpoints":
                return self.checkpoints
            case "$vaes":
                return self.vaes
            case "$loras":
                return self.loras
            case "$embeddings":
                return self.embeddings
            case "$output":
                return self.output_dir
