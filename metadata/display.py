import os
from PIL import Image
from metadata.png_metadata import parse_generation_parameters
from metadata.exif_metadata import has_exif, parse_exif


def compact(metadata: dict) -> dict:
    # we don't want to alter the original dictionary
    result = dict(metadata)

    # discard the filename because we should already have it
    if result.keys() & {"Filename"}:
        result.pop("Filename")

    # make showing the sizes more compact by using only one line each
    if result.keys() & {"Size-1", "Size-2"}:
        result["Size"] = f"{result.pop('Size-2')}x{result.pop('Size-1')}"
    elif result.keys() & {"Height", "Width"}:
        result["Size"] = f"{result.pop('Height')}x{result.pop('Width')}"

    if result.keys() & {"Hires resize-1", "Hires resize-2"}:
        hires_y = result.pop("Hires resize-1")
        hires_x = result.pop("Hires resize-2")

        if hires_x == 0 and hires_y == 0:
            result["Hires resize"] = "None"
        else:
            result["Hires resize"] = f"{hires_y}x{hires_x}"

    # remove LoRA if it exists and is empty
    if (result.keys() & {"LoRA"}) and (not result["LoRA"] or result["LoRA"] == "None"):
        result.pop("LoRA")

    return result


def displayable_metadata(image_filename: str) -> dict:
    if not os.path.isfile(image_filename):
        return {"source": "missing", "parameters": {}}

    pil_image = Image.open(image_filename)

    # we have PNG generation parameters (preferred, as it's what the txt2img
    # dropzone reads and we go via that for SendTo, and is directly tied to the image)
    if "parameters" in pil_image.info:
        return {
            "source": "png",
            "parameters": compact(
                parse_generation_parameters(pil_image.info["parameters"])
            ),
        }

    # EXIF data, probably a .jpeg, may well not include parameters,
    # but at least it's *something*
    if has_exif(image_filename):
        return {"source": "exif", "parameters": parse_exif(pil_image)}

    # we've got nothing
    return None
