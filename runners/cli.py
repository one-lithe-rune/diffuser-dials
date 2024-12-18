import re
import os
import fnmatch
import subprocess
import time

import sys
import inspect
from config.args import args

from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path

# from dict import dict_items
from config import paths


# generic util functions
# TODO: move somewhere else, or find builtin equivalents
def str_prefix(input: str, prefix: str) -> str:
    return input if input.startswith(prefix) else f"{prefix}{input}"


def list_lower(input: list[str]) -> list[str]:
    return [str(entry).lower() for entry in input]


def dict_key_lower(input: dict[str, object]) -> dict[str, object]:
    return {k.lower(): v for k, v in input.items()}


class ConfigDefinitionError(ValueError):
    pass


class ConfigInputValueError(ValueError):
    pass


class CliParameter(ABC):
    """Abstract base class for Config Parameters that will be passed to
    a Command Line generation tool
    """

    def __init__(self: type, entry: dict[str, object]):
        self._png_parameter = entry.get("png_parameter", None)
        self._required = entry.get("required", False)
        self._default = entry.get("default", "")
        self._displayable = entry.get("displayable", True)
        self._editable = entry.get("editable", True)
        try:
            self._cli_parameter = entry.get("cli_parameter", None)
        except KeyError:
            raise ConfigDefinitionError(
                f"The config entry {entry} is missing a 'cli_parameter' property"
            )
        try:
            self._display_source = entry["source"]
            self._source = (
                self._display_source.lower()
                if self._display_source
                else self._display_source
            )
        except KeyError:
            raise ConfigDefinitionError(
                f"The config entry {entry} is missing a 'source' property"
            )

    @property
    def displayable(self) -> bool:
        """answer whether the parameter should be displayed in the UI"""
        return self._displayable

    @property
    def editable(self) -> bool:
        """answer whether the parameter should be editable in the UI"""
        return self._editable

    @property
    def required(self) -> bool:
        """answer whether the parameter is required to have a value"""
        return self._required

    @property
    def options(self) -> list[str | int | float] | None:
        """Answers a list of options that can be selected for this parametr or
        None if there is no specific list of options
        """
        return None

    def for_default_display(self) -> tuple[str, str | int | float]:
        """Answers a tuple to include in the parameters to display as default
        when no image is selected"""
        if self.displayable and self._display_source:
            return (self._display_source, self._default, self.options)
        else:
            return ()

    @abstractmethod
    def for_cli(
        self, input_parameters: dict[str, str], ui_inputs: dict[str, object]
    ) -> tuple[str, str]:
        """Answers a tuple to include in the command line arguments sent to
        a command line generation tool for the passed input_parameters."""
        pass


class CliParameterDisplay(CliParameter):
    """Class for Config Parameters that will be displayed but will not
    be directly passed to a the command line generation tool. Use this
    when you have extracted parameters and you want to display where they
    are extracted from as part of the default parameter set.
    """

    def __init__(self: type, entry: dict[str, object]):
        self._required = entry.get("required", False)
        self._default = entry.get("default", "")
        self._editable = entry.get("editable", True)
        self._one_of = entry.get("one_of", None)
        self._displayable = True
        self._display_source = entry.get("source", None)
        self._source = self._display_source.lower()

    @property
    def options(self) -> list[str | int | float] | None:
        return self._one_of

    @property
    def required(self) -> bool:
        """answer whether the parameter is required to have a value"""
        return self._required

    @property
    def displayable(self) -> bool:
        """answer whether the parameter should be displayed in the UI"""
        return True

    def for_cli(
        self, input_parameters: dict[str, str], ui_inputs: dict[str, object]
    ) -> tuple[str, str]:
        """Answers an empty tuple that will not effect what will be sent
        to the generation tool."""
        return ()


class CliParameterHardCoded(CliParameter):
    def for_cli(
        self, input_parameters: dict[str, str], ui_inputs: dict[str, object]
    ) -> tuple[str, str]:
        if self._source:
            return (
                self._cli_parameter,
                self._source,
            )
        else:
            return [self._cli_parameter]


class CliParameterValue(CliParameter):
    """Class for Config Parameters to pass to a Command Line
    generation tool, that take a value of a specific type directly from
    the UI.
    """

    def __init__(self: type, entry: dict[str, object]):
        super().__init__(entry)
        self._type = entry.get("type", None)
        self._one_of = entry.get("one_of", None)
        self._range = entry.get("range", None)

    @property
    def options(self):
        return self._one_of

    def check_type(self, value: str | int | float) -> str | int | float:
        try:
            if self._type in [None, "str"]:
                return str(value)
            elif self._type == "int":
                return int(value)
            elif self._type == "float":
                return float(value)
            else:
                raise ConfigDefinitionError(
                    f"Unsupported type '{self._type}' requested"
                )
        except ValueError:
            raise ConfigInputValueError(
                f"Could not convert '{value}' to required type '{self._type}'"
            )

    def check_range(self, value: int | float) -> int | float:
        try:
            if self._range is None or value in range(self._range[0], self._range[1]):
                return value
            else:
                raise ConfigInputValueError(
                    f"value '{value}' not in required range {self._range}"
                )
        except IndexError:
            raise ConfigDefinitionError(f"'{self._range}' is not a range definition")

    def check_one_of(self, value: str | int | float) -> str | int | float:
        # TODO force every element of self._one_of list to lower()
        try:
            if self._one_of is None or str(value).lower() in self._one_of:
                return value
            else:
                raise ConfigInputValueError(
                    f"value '{value}' must be one of {self._one_of}"
                )
        except IndexError:
            raise ConfigDefinitionError(f"'{self._one_of}' is not a list definition")

    def for_cli(
        self, input_parameters: dict[str, str], ui_inputs: dict[str, object]
    ) -> tuple[str, str]:
        input_dict = dict_key_lower(input_parameters)
        result = input_dict.get(self._source, None)

        # answer an empty tuple when we don't have a value but its not required
        if (not self._required) and (result is None or str(result).strip() == ""):
            return ()

        # raise we don't have a value and it is required
        if self._required and (result is None or str(result).strip() == ""):
            raise ConfigInputValueError(
                f"A value for {self._png_parameter} is required"
            )

        result = self.check_type(result)
        result = self.check_range(result)
        result = self.check_one_of(result)

        if result is not None:
            return (self._cli_parameter, str(result))
        else:
            return ()


class CliParameterExtract(CliParameterValue):
    """Class for Config Parameters to pass to a Command Line generation tool,
    where the value to be passed to the tool needs to be extracted using a
    regular expression
    """

    def __init__(self: type, entry: dict[str, object]):
        super().__init__(entry)
        # since we're extracting from something that is presumably displayed
        # it doesn't make sense to display the extract value too
        self._displayable = False

        if "regex" not in entry:
            raise ConfigDefinitionError(
                f"The config entry {entry} is missing a 'regex' property"
            )

        self._regex = entry["regex"]

    def for_cli(
        self, input_parameters: dict[str, str], ui_inputs: dict[str, object]
    ) -> tuple[str, str]:
        input_dict = dict_key_lower(input_parameters)
        result = input_dict.get(self._source, None)

        # answer an empty tuple when we don't have a value but its not required
        if (not self._required) and (result is None or str(result).strip() == ""):
            return ()

        # raise we don't have a value and it is required
        if self._required and (result is None or str(result).strip() == ""):
            raise ConfigInputValueError(
                f"A value for {self._png_parameter} is required"
            )

        search = re.search(self._regex, result)

        if search:
            match = search.groups()[0] if search.groups() else search.group()
            result = match if match else None

        # raise we we're able to extract a value
        if result is None or str(result).strip() == "":
            raise ConfigInputValueError(
                f"Could not extract a value for '{self._cli_parameter}' from '{self._source}'"
            )

        result = self.check_type(result)
        result = self.check_range(result)
        result = self.check_one_of(result)

        if result is not None and str(result).strip() != "":
            return (self._cli_parameter, str(result))
        else:
            return ()


class CliParameterDir(CliParameter):
    """Class for Config Parameters to pass to a Command Line generation tool,
    where the parameter represents a directory path
    """

    def for_cli(
        self, input_parameters: dict[str, str], ui_inputs: dict[str, object]
    ) -> tuple[str, str]:
        result = paths.for_placeholder(self._source)

        # if required we do care
        if self._required and (result is None or str(result).strip() == ""):
            raise ConfigInputValueError(
                f"A value for {self._png_parameter} is required"
            )

        if (result is not None) and str(result).strip() != "":
            return (
                self._cli_parameter,
                str(result),
            )
        else:
            return ()


class CliParameterFile(CliParameter):
    """Class for Config Parameters to pass to a Command Line generation tool,
    where the parameter represents a file name
    """

    def __init__(self: type, entry: dict[str, object]):
        super().__init__(entry)
        self._base_path = entry.get("base_path", None)
        self._case_sensitive = entry.get("case_sensitive", False)
        self._extensions = entry.get("extensions", None)
        if self._extensions is not None and isinstance(self._extensions, str):
            self._extensions = [self._extensions]
        self._extensions = list_lower(
            str_prefix(str(entry), ".") for entry in self._extensions
        )
        self._generate = entry.get("generate", None)

        default_source = entry.get("default_from_arg", None)
        self._default_file = (
            args.__dict__[default_source] if default_source in args.__dict__ else None
        )
        self._force_default = entry.get("force_default", False)

    def for_default_display(self):
        """If displayable answers the first file name, matching the first
        extension in folder specified by base_path. Other wise"""

        if self._displayable:
            if self._base_path is not None:
                path: Path = paths.for_placeholder(self._base_path) / self._default
            else:
                path: Path = Path(self._default)

            # TODO: Not sure these case shenanigans are necssary or working
            glob = f"*{self._extensions[0]}" if self._extensions is not None else "*"
            re_flag = re.IGNORECASE if not self._case_sensitive else 0

            regex = re.compile(fnmatch.translate(str(glob)), re_flag)
            try:
                files = [
                    Path(file).stem
                    for file in os.listdir(str(path))
                    if regex.match(file)
                ]
            except OSError:
                files = []

            if self._default_file and Path(self._default_file).stem in files:
                return (self._display_source, Path(self._default_file).stem, files)
            elif self._force_default and len(files) > 0:
                return (self._display_source, files[0], files)
            else:
                return (self._display_source, "", [""] + files)

        return ()

    def for_cli(
        self, input_parameters: dict[str, str], ui_inputs: dict[str, object]
    ) -> tuple[str, str]:
        input_dict = dict_key_lower(input_parameters)

        if self._generate is not None:
            # TODO: improve what is generated for the file name
            subdir = ui_inputs.get("subdir", "")
            result = (Path(subdir) / f"{int(time.time())}").with_suffix(
                self._extensions[0]
            )
        else:
            result: str = input_dict.get(self._source, None)

        # when not required, we don't care if there is nothing specified
        if (not self._required) and (result is None or str(result).strip() == ""):
            return ()

        # if a base_path is set then we want the full path including it
        if self._base_path is not None:
            result: Path = paths.for_placeholder(self._base_path) / result
        else:
            result: Path = Path(result)

        # make sure we answer the path with a valid a extension, if listed
        # TODO: We should check for all extension in the next phase. This
        # doesn't allow that
        if self._extensions is not None and (
            result.suffix == "" or result.suffix.lower() not in self._extensions
        ):
            result = result.with_suffix(f".{self._extensions[0].removeprefix('.')}")

        print(f"path: {result}")
        # check path exists
        path = result.parent
        if not path.exists():
            raise ConfigInputValueError(
                f"The path to '{str(result)}' for {self._cli_parameter} does not exist"
            )

        # check file exists for files we're not generating
        if self._generate is None:
            if self._case_sensitive and not result.exists():
                raise ConfigInputValueError(
                    f"The file '{str(result)}' for {self._cli_parameter} does not exist"
                )

            if not self._case_sensitive:
                regex = re.compile(fnmatch.translate(str(result.name)), re.IGNORECASE)
                files = [file for file in os.listdir(path) if regex.match(file)]
                if len(files) == 0:
                    raise ConfigInputValueError(
                        f"The file '{str(result)}' for {self._cli_parameter} does not exist"
                    )
                else:
                    result = path / files[0]

        return (
            self._cli_parameter,
            str(result),
        )


# TODO: Pull this abstract base class out into its own separate file
# once we have more than a single Runner subclass. This exists only
# for type hinting right now
class Runner(ABC):
    """
    Base class an object that can parse and run a configuration definition
    """

    @abstractmethod
    def get_defaults(self):
        pass


class CliRunner(Runner):
    """
    Class that can parse and run a CLI configuration definition
    """

    def __init__(self, config: dict[str, object]):
        self.name: str = config.get("name", None)
        if self.name is None:
            raise ConfigDefinitionError(f"No name defined for config '{config}'")

        if not config.get("connection", None) == "CLI":
            raise ValueError("Not a CLI config")

        config_parameters: dict[str, object] = config.get("parameters", None)
        if config_parameters is None:
            raise ConfigDefinitionError(
                f"No parameters defined for config '{self.name}'"
            )

        commands: dict[str, object] = config.get("commands", None)
        self._command = commands.get(sys.platform, commands.get("default", None))
        if self._command is None:
            raise ConfigDefinitionError(
                f"No command defined in config '{self.name}' for '{sys.platform}' or 'default'"
            )

        # get the possible parameter classes
        parameter_classes: dict[str, CliParameter] = {
            name.replace("CliParameter", "").lower(): cls
            for name, cls in inspect.getmembers(
                sys.modules[__name__],
                lambda member: inspect.isclass(member)
                and not inspect.isabstract(member),
            )
            if cls.__module__ == __name__ and name.startswith("CliParameter")
        }

        self._parameters: list[CliParameter] = []
        for arg in config_parameters:
            try:
                param_class = arg.get("class", "").lower()
                if param_class not in parameter_classes.keys():
                    raise ConfigDefinitionError(
                        f"No valid parameter class defined for {arg}"
                    )
                self._parameters.append(parameter_classes[param_class](arg))

            except (ConfigDefinitionError, ConfigInputValueError) as e:
                print(f"Config '{self.name}' parseError: {e.args}")
                continue

    def get_command(
        self, inputs: dict[str, str], ui_inputs: dict[str, object]
    ) -> list[str]:
        result = []
        for parameter in self._parameters:
            try:
                result.extend(parameter.for_cli(inputs, ui_inputs))
            except (ConfigDefinitionError, ConfigInputValueError) as e:
                print(f"Value '{parameter._cli_parameter}' parseError: {e.args}")
                if parameter.required:
                    raise ValueError(
                        f"Could not generate a command line for '{self.name}'"
                    )

        if len(result) > 0:
            return [self._command] + result
        else:
            raise ValueError(f"Could not generate a command line for '{self.name}'")

    def get_defaults(self):
        result: list[list[str, str | int | float]] = []
        for parameter in self._parameters:
            try:
                if parameter.displayable:
                    result.append(parameter.for_default_display())
            except (ConfigDefinitionError, ConfigInputValueError) as e:
                print(f"Value '{parameter._cli_parameter}' parseError: {e.args}")
                if parameter.required:
                    raise ValueError(
                        f"Could not generate a default parameter for '{self.name}'"
                    )

        result = [list(entry) for entry in result if entry]

        if len(result) > 0:
            return result
        else:
            raise ValueError(f"Could not generate default parameters for '{self.name}'")

    def run(self, inputs: list[list], ui_inputs: dict[str, object]):
        subprocess.run(self.get_command(inputs, ui_inputs))
