# ![a logo of rotatable black knob with orange and blue edges around its circumferance](./images/logo-very-small.png) &nbsp; Diffuser Dials

## Motivation

My medium term aim, in this repo, is make a UI application for Stable Diffusion image generation backends that **doesn't** include those backends themselves. Instead making it able to talk to various different ones, including those with [A1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) compatible REST APIs, generation run through raw Python scripts such as [Diffusers](https://github.com/huggingface/diffusers) or [SHARK-Turbine](https://github.com/nod-ai/SHARK-Turbine).

Currently the interface for this is some code I have contributed to [SHARK](https://github.com/nod-ai/SHARK) pulled out into its own Python application, because I would like to use it for not-SHARK stuff and apparently I have terminal [NIH](https://en.wikipedia.org/wiki/Not_invented_here) syndrome.

At the moment the application as a whole only supports using [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) and only for text to image. So you'll need that on your path somewhere if you want anything generation-y to happen.

## Requirements

I'm currently working on this on Linux, using Python 3.11.  Those are your best bets, but it *should* work on Windows and Mac, however getting it setup on those is left as an exercise for the reader, and I haven't tested them.

I don't have much idea about other Python versions atm. Sorry.

And you'll need both [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) and a suitable stable-diffusion model checkpoint in safetensors format from [Huggingface](https://huggingface.co/runwayml/stable-diffusion-v1-5), [Civitai](https://civitai.com/) or similar.

## Setup and Usage (Linux)

If you're feeling brave or curious enough to try this, grab [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) build it and put it on your path, then clone this repo, and create create a suitable virtual environment:

```bash
# Make sure you are in the folder you cloned the repo to
# Replace python3.11 without however python 3.11 is named on your system

python3.11 -m venv .venv
source ./.venv/bin/activate
```

Then install the requirements using `pip` in the usual way:

```bash
pip install -r requirements.txt
```

Then to start the application or look at the command line arguments:

```bash
# Make sure you've activated the correct virtual environment just like you did after creating it

# See the command line options
python ./diffuser-dials.py --help

# See run the application, you'll need to then connnect to it frpm your favourite (modern) web browser
python ./diffuser-dials.py
```

## (Very) vague roadmap

- [ ] Settings tab
  - [ ] Command line arguments in the UI
  - [ ] Backend config.
  - [ ] Model configs.
- [ ] Support more backends than [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp).
- [ ] Multiple root folders (or similar).
- [ ] Prompt templating.


## Contributing

Throw up a PR if you're feeling eager, or you have a bug fix. I'll probably want to get things in a better state before trying to merge anything big, but maybe your feature is super cool!

## Copyright

    Copyright 2024 Stefan Kapusniak and CONTRIBUTERS (see accompanying file)

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

## Additional Notice and Attributions

    Some parts derived from code by other NodAI/SHARK contributers originally
    licensed under the Apache License Version 2.0 with LLVM exception.

    See:
    https://github.com/nod-ai/SHARK
    https://github.com/nod-ai/SHARK/graphs/contributors

