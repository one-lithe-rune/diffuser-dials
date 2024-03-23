import re
import os
import fnmatch
import time

from config import paths


class CliRunner:
    def __init__(self, config: dict):
        if not config["connection"] == "CLI":
            raise ValueError()

        self.config = config

    def input_value(self, input_parameters: dict, key: str):
        return input_parameters[key] if key in input_parameters else ""


    # TODO: Kill it with fire then reimplement in a much less scruffy way
    def get_command(self, source: list[list], ui_subdir: str) -> str:
        # convert source to parameters dictionary
        input_parameters = {row[0].lower():row[1] for row in source}

        output_parameters=[]
        for argument, sourcing in self.config["argument_map"].items():
            param_value = None
            if "from" in sourcing:
                if isinstance(sourcing["from"], list):
                    from_sources  = [entry.lower() for entry in sourcing["from"] ]
                else:
                    from_sources = [sourcing["from"].lower()]
            else:
                from_sources = [None]

            try:
                for from_source in from_sources:
                    print(f"argument: {argument}")
                    if from_source in input_parameters or from_source is None:
                        print(f"from_source: {from_source}")
                        match sourcing["type"]:
                            case "FixedValue":
                                param_value = from_source
                            case "ParamStrValue":
                                value = self.input_value(input_parameters, from_source)
                                param_value = value if (not "limit" in sourcing) or (value in sourcing["limit"]) else None
                            case "ParamUintValue" | "ParamIntValue":
                                value = int(self.input_value(input_parameters, from_source))
                                if "range" not in sourcing or value in range(sourcing["range"][0], sourcing["range"][1]):
                                    param_value = value
                            case "ParamFloat32Value":
                                value = float(self.input_value(input_parameters, from_source))
                                if "range" not in sourcing or value in range(sourcing["range"][0], sourcing["range"][1]):
                                    param_value = value
                            case "FullDirPath":
                                path = paths.for_placeholder(sourcing["base_path"])
                                param_value = str(path) if path.exists() else None
                            case "FullFilePathForceExtension":
                                input_value = self.input_value(input_parameters, from_source)
                                path = paths.for_placeholder(sourcing["base_path"])
                                if path.exists():
                                    # TODO: rewrite as a list comprehension
                                    # find in the base_path for all specified extensions
                                    for extension in sourcing["extensions"]:
                                        # case insenstive because we've already normalised 'from' that way
                                        # and we don't know what platform the source originally came from
                                        regex = re.compile(fnmatch.translate(f"{os.path.splitext(input_value)[0]}.{extension}"), re.IGNORECASE)
                                        for filename in os.listdir(path):
                                            if regex.match(filename):
                                                param_value = str(path / filename)
                                                break
                            case "GenerateFilenameFullPath":
                                path = paths.for_placeholder(sourcing["base_path"])
                                extension = sourcing["extension"]
                                # TODO: use something saner as the filename
                                param_value = str(path / ui_subdir / f"{int(time.time())}.{extension}")
                            case "ParamIntValueExtract":
                                search = re.search(sourcing["regex"], self.input_value(input_parameters, from_source))
                                match = search.groups()[0] if search.groups() else search.group()
                                param_value = int(match) if match else None
                            case "ParamValueExtract":
                                search = re.search(sourcing["regex"], self.input_value(input_parameters, from_source))
                                match = search.groups()[0] if search.groups() else search.group()
                                param_value = match if (not "limit" in sourcing) or (match in sourcing["limit"]) else None

            except Exception as e:
                print(f"ParseError: {e},{argument}")

            if not param_value == None:
                output_parameters.extend([argument, param_value])

        # only include the executable if we managed to get parameters
        # TODO: make this so that we only include if all required parameters
        if len(output_parameters) > 0:
            output_parameters = [self.config["command"]["default"]] + output_parameters

        return [str(param) for param in output_parameters]

