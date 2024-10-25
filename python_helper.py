from py4godot.classes import gdclass
from py4godot.classes.core import NodePath, String, StringName, Color
from py4godot.classes.Node.Node import Node
from py4godot.classes.Label.Label import Label
from py4godot.classes.LineEdit.LineEdit import LineEdit
from py4godot.classes.TextEdit.TextEdit import TextEdit
from py4godot.classes.Button.Button import Button
from py4godot.classes.HSlider.HSlider import HSlider
from py4godot.classes.Button.Button import Button
from py4godot.classes.OptionButton.OptionButton import OptionButton
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
		self.downscale_checkbox = Button.cast(self.get_node(NodePath.new2("%DownscaleCheckBox")))
		self.original_checkbox = Button.cast(self.get_node(NodePath.new2("%OriginalCheckBox")))
		self.upscale_checkbox = Button.cast(self.get_node(NodePath.new2("%UpscaleCheckBox")))
		self.kcentroid_checkbox = Button.cast(self.get_node(NodePath.new2("%KCentroidCheckBox")))
		self.colors_count_slider = HSlider.cast(self.get_node(NodePath.new2("%ColorsCountSlider")))
		self.downscale_factor_slider = HSlider.cast(self.get_node(NodePath.new2("%DownscaleFactorSlider")))
		self.matrix_size_option = OptionButton.cast(self.get_node(NodePath.new2("%MatrixSizeOption")))
		self.dithering_strength_slider = HSlider.cast(self.get_node(NodePath.new2("%DitheringStrengthSlider")))
		
		self.generated_image = TextureRect.cast(self.get_node(NodePath.new2("%GeneratedImage")))
		self.generated_image_full = TextureRect.cast(self.get_node(NodePath.new2("%GeneratedImageFull")))
		
		self.generate_button = Button.cast(self.get_node(NodePath.new2("%GenerateButton")))
		self.generate_button.pressed.connect(self.generate_button_pressed)
	
	# Saves a PIL image to the outputs folder
	def save_image(self, image, postfix=""):
		os_instance = OS.get_instance()
		outputs_folder_path = os_instance.get_user_data_dir() + "/outputs"
		
		if not DirAccess.dir_exists_absolute(outputs_folder_path):
			DirAccess.make_dir_absolute(outputs_folder_path)
		
		time_instance = Time.get_instance()
		file_name = time_instance.get_datetime_string_from_system(True, True).replace(":", "_") + postfix + ".png"
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
		
		show_original = False
		if self.palettize_checkbox.button_pressed:
			downscale = self.downscale_checkbox.button_pressed
			show_original = self.original_checkbox.button_pressed
			upscale = self.upscale_checkbox.button_pressed
			kcentroid = self.kcentroid_checkbox.button_pressed
			scale = int(self.downscale_factor_slider.value)
			# TODO: palette options
			paletteDropdown = "None"
			paletteURL = ""
			palette = None
			clusters = int(self.colors_count_slider.value)
			dither = self.matrix_size_option.selected
			ditherStrength = int(self.dithering_strength_slider.value)
			processed = run_palettize(processed, downscale, show_original, upscale, kcentroid, scale, paletteDropdown, paletteURL, palette, clusters, dither, ditherStrength)
		
		image = processed.images[0]
		
		# Save to folder of generated images
		image_path = self.save_image(image)
		
		# Display the image
		#self.show_debug_image()
		if show_original and len(processed.images) == 2:
			# Save the original image
			original_image = processed.images[1]
			image_path = self.save_image(original_image, " original")
			# Display the original image
			loaded_image = GDImage.load_from_file(image_path)
			texture = ImageTexture.create_from_image(loaded_image)
			self.generated_image.texture = texture
			self.generated_image_full.texture = texture
		else:
			loaded_image = GDImage.load_from_file(image_path)
			texture = ImageTexture.create_from_image(loaded_image)
			self.generated_image.texture = texture
			self.generated_image_full.texture = texture

	def generate_button_pressed(self):
		if not os.path.isfile(self.model_path_line.text):
			print("Invalid file path: " + self.model_path_line.text)
			return
		
		self.generate_image()

	def show_debug_image(self):
		img = GDImage.create(256, 256, False, 5)
		img.fill(Color.new3(1, 0, 0))
		self.generated_image.texture = ImageTexture.create_from_image(img)
