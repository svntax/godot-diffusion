from py4godot.classes import gdclass
from py4godot.classes.core import NodePath, String, StringName, Color
from py4godot.classes.Node.Node import Node
from py4godot.classes.Label.Label import Label
from py4godot.classes.LineEdit.LineEdit import LineEdit
from py4godot.classes.TextEdit.TextEdit import TextEdit
from py4godot.classes.Button.Button import Button
from py4godot.classes.HSlider.HSlider import HSlider
from py4godot.classes.Button.Button import Button
from py4godot.classes.TextureRect.TextureRect import TextureRect
from py4godot.classes.Image.Image import Image as GDImage
from py4godot.classes.ImageTexture.ImageTexture import ImageTexture
from py4godot.classes.DirAccess.DirAccess import DirAccess
from py4godot.classes.OS.OS import OS
from py4godot.classes.Time.Time import Time

from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import os.path
import random, sys

sys.path.append("/scripts")
from scripts.palettize import run_palettize

@gdclass
class python_helper(Node):
	
	# Saves a PIL image to the outputs folder
	def save_image(self, image):
		os_instance = OS.get_instance()
		outputs_folder_path = os_instance.get_user_data_dir() + "/outputs"
		
		if not DirAccess.dir_exists_absolute(outputs_folder_path):
			DirAccess.make_dir_absolute(outputs_folder_path)
		
		time_instance = Time.get_instance()
		file_name = time_instance.get_datetime_string_from_system(True, True).replace(":", "_") + ".png"
		file_path = outputs_folder_path + "/" + file_name
		image.save(file_path)
		
		return file_path

	def generate_image(self):
		model_path = self.model_path_line.text
		prompt = self.positive_prompt.text
		seed = random.randint(0, sys.maxsize)
		seed_text: String = String.new1(self.seed_input.text)
		if seed_text.is_valid_int():
			seed = int(self.seed_input.text)
		
		pipe = StableDiffusionPipeline.from_single_file(model_path, torch_dtype=torch.float16,
			local_files_only=True,
			use_safetensors=True,
			add_watermarker=False)
		pipe.to("cuda")
		
		generator = torch.Generator(device="cuda").manual_seed(seed)
		processed = pipe(prompt,
			negative_prompt=self.negative_prompt.text,
			width=self.width_slider.value,
			height=self.height_slider.value,
			num_inference_steps=self.sampling_steps_slider.value,
			guidance_scale=self.cfg_scale_slider.value,
			generator=generator)
		
		if self.palettize_checkbox.button_pressed:
			downscale = True
			original = False
			upscale = True
			kcentroid = True
			scale = 8
			paletteDropdown = "None"
			paletteURL = ""
			palette = None
			clusters = 24
			dither = 0
			ditherStrength = 0
			processed = run_palettize(processed, downscale, original, upscale, kcentroid, scale, paletteDropdown, paletteURL, palette, clusters, dither, ditherStrength)
		
		image = processed.images[0]
		
		# Save to folder of generated images
		image_path = self.save_image(image)
		
		# Display the image
		#self.show_debug_image()
		loaded_image = GDImage.load_from_file(image_path)
		texture = ImageTexture.create_from_image(loaded_image)
		self.generated_image.texture = texture
		self.generated_image_full.texture = texture

	def _ready(self) -> None:
		self.positive_prompt = TextEdit.cast(self.get_node(NodePath.new2("%PositivePrompt")))
		self.negative_prompt = TextEdit.cast(self.get_node(NodePath.new2("%NegativePrompt")))
		self.model_path_line = LineEdit.cast(self.get_node(NodePath.new2("%ModelPath")))
		self.width_slider = HSlider.cast(self.get_node(NodePath.new2("%WidthSlider")))
		self.height_slider = HSlider.cast(self.get_node(NodePath.new2("%HeightSlider")))
		self.sampling_steps_slider = HSlider.cast(self.get_node(NodePath.new2("%SamplingStepsSlider")))
		self.cfg_scale_slider = HSlider.cast(self.get_node(NodePath.new2("%CFGScaleSlider")))
		self.seed_input = LineEdit.cast(self.get_node(NodePath.new2("%SeedInput")))
		self.palettize_checkbox = Button.cast(self.get_node(NodePath.new2("%PalettizeCheckBox")))
		self.generated_image = TextureRect.cast(self.get_node(NodePath.new2("%GeneratedImage")))
		self.generated_image_full = TextureRect.cast(self.get_node(NodePath.new2("%GeneratedImageFull")))
		
		self.generate_button = Button.cast(self.get_node(NodePath.new2("%GenerateButton")))
		self.generate_button.pressed.connect(self.generate_button_pressed)

	def generate_button_pressed(self):
		if not os.path.isfile(self.model_path_line.text):
			print("Invalid file path: " + self.model_path_line.text)
			return
		
		self.generate_image()

	def show_debug_image(self):
		img = GDImage.create(256, 256, False, 5)
		img.fill(Color.new3(1, 0, 0))
		self.generated_image.texture = ImageTexture.create_from_image(img)
