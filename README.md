# godot-diffusion
Run diffusion models directly within Godot.

This project is made with Godot 4.3 and uses the GDExtension plugin [py4godot](https://github.com/niklas2902/py4godot) for running Python.

## Setup
Clone this repository, and then install py4godot 1.0.0-alpha2 into `/addons/` in the root folder (see the README in the py4godot repository for more info).

### Windows
To install Python packages, follow the setup instructions from py4godot here: https://github.com/niklas2902/py4godot/wiki/Installing-packages-for-python

You should have pip installed in `addons\py4godot\cpython-3.12.4-windows64\python`

In this directory, run the following to set up a virtual environment for Python:
```
python -m venv .venv
```
And then activate the environment:
```
.venv\Scripts\activate
```
Then install the [Diffusers](https://huggingface.co/docs/diffusers/en/installation) library with the following command:
```
python -m pip install diffusers["torch"] transformers
```
And to set up CUDA for [PyTorch](https://pytorch.org/get-started/locally/), run the following:
```
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```
To set up the [Palettize](https://github.com/Astropulse/sd-palettize) tool, install the following packages:
```
python -m pip install git+https://www.github.com/hbldh/hitherdither
python -m pip install opencv-python
```

## Running the project
![godot_diffusion_screenshot](https://github.com/user-attachments/assets/fe651c5d-b310-419a-8aae-48bfd8658353)

To generate images, run the main scene, and then select a `.safetensors` model to load and press "Generate".

### Palettize
The [Palettize](https://github.com/Astropulse/sd-palettize) tool by Astropulse has been edited to work with this project's setup. It works with any model, but check out the standalone [Retro Diffusion Model](https://astropulse.gumroad.com/l/RetroDiffusionModel) to see high quality pixel art results.

## How it works
The scene `Main.tscn` is essentially an interface for running diffusion models with Diffusers. It uses a helper node with `python_helper.py` handling the connections between the UI and Python.

The Palettize tool in `scripts/palettize.py` has a function `run_palettize()` that the main scene runs if the tool is enabled by the user.
