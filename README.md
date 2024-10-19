# godot-diffusion
Run Stable Diffusion directly within Godot.

## Setup
This project is made with Godot 4.3 and uses the GDExtension plugin [py4godot](https://github.com/niklas2902/py4godot) for running Python.

First clone this repository, and then install py4godot 1.0.0-alpha2 into `/addons/` in the root folder (see the README in the py4godot repository for more info).

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
To set up the [Palettize](https://github.com/Astropulse/sd-palettize) tool, run the following:
```
python -m pip install git+https://www.github.com/hbldh/hitherdither
python -m pip install opencv-python
```