import re

re_param_code = r'\s*([\w ]+):\s*("(?:\\"[^,]|\\"|\\|[^\"])+"|[^,]*)(?:,|$)'
re_param = re.compile(re_param_code)
re_imagesize = re.compile(r"^(\d+)x(\d+)$")

# Translating samplers between backends is tricky
# these are unlikely to be 100% correct
DIFFUSER_SAMPLERS = {
    "PNDM": "pndm",
    "HeunDiscrete": "heun discrete",
    "DDIM": "ddim",
    "DDPM": "ddpm",
    "EulerDiscrete": "euler discrete",
    "EulerAncestralDiscrete": "euler_a discrete",
    "SharkEulerDiscrete": "euler discrete",
    "SharkEulerAncestralDiscrete": "euler_a discrete",
    "LCMScheduler": "lcm",
    "DPMSolverMultistep": "dpm++2m",
    "DPMSolverMultistepKarras": "dpm++2m karras",
    "DPMSolverMultistep++": "dpm++2mv2 discrete",
    "DPMSolverMultistepKarras++": "dpm++2mv2 karras",
    "DPMSolverSDE": "dpm++2s_a discrete",
    "DPMSolverSDEKarras": "dpm++2s_a karras",
    "KDPM2DiscreteScheduler": "dpm discrete",
}


def parse_generation_parameters(x: str):
    res = {}
    prompt = ""
    negative_prompt = ""
    done_with_prompt = False

    *lines, lastline = x.strip().split("\n")
    if len(re_param.findall(lastline)) < 3:
        lines.append(lastline)
        lastline = ""

    for _i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("Negative prompt:"):
            done_with_prompt = True
            line = line[16:].strip()

        if done_with_prompt:
            negative_prompt += ("" if negative_prompt == "" else "\n") + line
        else:
            prompt += ("" if prompt == "" else "\n") + line

    res["Prompt"] = prompt
    res["Negative prompt"] = negative_prompt

    for k, v in re_param.findall(lastline):
        v = v[1:-1] if v[0] == '"' and v[-1] == '"' else v
        m = re_imagesize.match(v)
        if m is not None:
            res[k + "-1"] = m.group(1)
            res[k + "-2"] = m.group(2)
        else:
            res[k] = v

    # Add a placeholders for parameters that might be missing
    res["Clip skip"] = res.get("Clip skip", None)
    res["VAE"] = res.get("VAE", "")

    # attempt to make sampler names consistent
    sampler = res.get("Sampler", None)
    if sampler is not None and sampler in DIFFUSER_SAMPLERS:
        res["Sampler"] = DIFFUSER_SAMPLERS[sampler]

    # Some backends have parameters that others put in the prompt
    # if they support them
    lora = res.get("LoRA", None)
    if lora is not None and lora != "None":
        res["Prompt"] = " ".join([res["Prompt"], f"<lora:{lora}>"])

    hypernet = res.get("Hypernet", None)
    if hypernet is not None:
        res[
            "Prompt"
        ] += f"""<hypernet:{hypernet}:{res.get("Hypernet strength", "1.0")}>"""

    if "Hires resize-1" not in res:
        res["Hires resize-1"] = 0
        res["Hires resize-2"] = 0

    return res
