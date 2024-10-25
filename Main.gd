extends Control

@onready var model_path: LineEdit = %ModelPath
@onready var file_dialog: FileDialog = %FileDialog
@onready var generated_image: TextureRect = %GeneratedImage
@onready var full_view_container: ScrollContainer = %FullViewContainer
@onready var width_value_label: Label = %WidthValueLabel
@onready var height_value_label: Label = %HeightValueLabel
@onready var sampling_steps_label: Label = %SamplingStepsLabel
@onready var cfg_scale_label: Label = %CFGScaleLabel

@onready var palettize_parameters_container: PanelContainer = %PalettizeParametersContainer
@onready var colors_count_label: Label = %ColorsCountLabel
@onready var downscale_factor_label: Label = %DownscaleFactorLabel
@onready var dithering_strength_label: Label = %DitheringStrengthLabel

func _ready():
	full_view_container.hide()

func _on_load_model_button_pressed() -> void:
	file_dialog.visible = true

func _on_file_dialog_file_selected(path: String) -> void:
	model_path.text = path

func _on_view_image_button_pressed() -> void:
	full_view_container.show()

func _on_close_full_view_button_pressed() -> void:
	full_view_container.hide()

func _on_width_slider_value_changed(value: float) -> void:
	width_value_label.text = str(value)

func _on_height_slider_value_changed(value: float) -> void:
	height_value_label.text = str(value)

func _on_sampling_steps_slider_value_changed(value: float) -> void:
	sampling_steps_label.text = str(value)

func _on_cfg_scale_slider_value_changed(value: float) -> void:
	cfg_scale_label.text = str(value)

func _on_open_outputs_button_pressed() -> void:
	var outputs_folder_path = OS.get_user_data_dir() + "/outputs"
	if not DirAccess.dir_exists_absolute(outputs_folder_path):
		DirAccess.make_dir_absolute(outputs_folder_path)
	
	OS.shell_open(ProjectSettings.globalize_path(outputs_folder_path))

func _on_palettize_menu_button_pressed() -> void:
	palettize_parameters_container.visible = !palettize_parameters_container.visible

func _on_colors_count_slider_value_changed(value: float) -> void:
	colors_count_label.text = str(value)

func _on_downscale_factor_slider_value_changed(value: float) -> void:
	downscale_factor_label.text = str(value)

func _on_dithering_strength_slider_value_changed(value: float) -> void:
	dithering_strength_label.text = str(value)
