# ![a logo of rotatable black knob with orange and blue edges around its circumferance](./images/logo-very-small.png) &nbsp; Diffuser Dials 

## Motivation

My medium term aim, in this repo, is make a UI application for Stable Diffusion image generation backends that **doesn't** include those backends themselves. Instead making it able to talk to various different ones, including those with [A1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) compatible REST APIs, generation run through raw Python scripts such as [Diffusers](https://github.com/huggingface/diffusers) or [SHARK-Turbine](https://github.com/nod-ai/SHARK-Turbine), or by running console applications like [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp), or calling shared library functions (probably stable-diffusion.cpp again)

For now this is mostly just some of the User Interface code I have contributed to [SHARK](https://github.com/nod-ai/SHARK) pulled out into its own Python application, because I would like to use it for not-SHARK stuff and apparently I have terminal [NIH](https://en.wikipedia.org/wiki/Not_invented_here) syndrome. 

**Currently this applictions doesn't do anything other than let you look at images you might already on your system from your web browser.**

## Requirements

I'm currently working on this on Linux, using Python 3.11.  Those are your best bets, but it *should* work on Windows and Mac, however getting it setup on those is left as an exercise for the reader, and I haven't tested those.

I don't have much idea about other Python versions atm. Sorry.

## Setup and Usage (Linux)

Unless you have an attachment to the [SHARK](https://github.com/nod-ai/SHARK) output gallery UI, you probably don't want to use this in the current state. But if you're feeling brave or curious, after cloning the repo,  create a suitable virtual environment:

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

## Tentative Starting Roadmap
- [ ] Report Gradio bugs.
- [ ] Option to launch the web browser (default?).
- [ ] Fix 'Open Folder' Request checking.
- [ ] Initial backend config system.
- [ ] Config for [stable-diffusion-cpp](https://github.com/leejet/stable-diffusion.cpp) CLI.
- [ ] An actual Txt2Img generation button. That generates.
- [ ] Settings tab.

## Contributing

At the moment I'm still working on the core stuff, so I don't have things set up so there are obvious attachment points. But throw up a PR if you're feeling eager, or you have a bug fix. I'll probably want to get things in a better state before trying to merge anything big, but maybe your feature is super cool!

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
    
    