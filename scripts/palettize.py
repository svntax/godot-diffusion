import hitherdither

import cv2
import numpy as np
from PIL import Image
import os, requests
from io import BytesIO
from itertools import product

pal_path='./extensions/sd-palettize/palettes/'

def refreshPalettes():
	palettes = ["None", "Automatic"]
	file_names = [fn for fn in sorted(os.listdir(pal_path)) if ".preview." not in fn]
	palettes.extend(file_names)
	return palettes

def adjust_gamma(image, gamma=1.0):
	# Create a lookup table for the gamma function
	gamma_map = [255 * ((i / 255.0) ** (1.0 / gamma)) for i in range(256)]
	gamma_table = bytes([(int(x / 255.0 * 65535.0) >> 8) for x in gamma_map] * 3)

	# Apply the gamma correction using the lookup table
	return image.point(gamma_table)

def kCentroid(image: Image, width: int, height: int, centroids: int):
	image = image.convert("RGB")
	downscaled = np.zeros((height, width, 3), dtype=np.uint8)
	wFactor = image.width/width
	hFactor = image.height/height
	for x, y in product(range(width), range(height)):
			tile = image.crop((x*wFactor, y*hFactor, (x*wFactor)+wFactor, (y*hFactor)+hFactor)).quantize(colors=centroids, method=1, kmeans=centroids).convert("RGB")
			color_counts = tile.getcolors()
			most_common_color = max(color_counts, key=lambda x: x[0])[1]
			downscaled[y, x, :] = most_common_color
	return Image.fromarray(downscaled, mode='RGB')

def determine_best_k(image, max_k):
	# Convert the image to RGB mode
	image = image.convert("RGB")

	# Prepare arrays for distortion calculation
	pixels = np.array(image)
	pixel_indices = np.reshape(pixels, (-1, 3))

	# Calculate distortion for different values of k
	distortions = []
	for k in range(1, max_k + 1):
		quantized_image = image.quantize(colors=k, method=2, kmeans=k, dither=0)
		centroids = np.array(quantized_image.getpalette()[:k * 3]).reshape(-1, 3)

		# Calculate distortions
		distances = np.linalg.norm(pixel_indices[:, np.newaxis] - centroids, axis=2)
		min_distances = np.min(distances, axis=1)
		distortions.append(np.sum(min_distances ** 2))

	# Calculate the rate of change of distortions
	rate_of_change = np.diff(distortions) / np.array(distortions[:-1])

	# Find the elbow point (best k value)
	if len(rate_of_change) == 0:
		best_k = 2
	else:
		elbow_index = np.argmax(rate_of_change) + 1
		best_k = elbow_index + 2

	return best_k

# Runs cv2 k_means quantization on the provided image with "k" color indexes
def palettize(input, colors, palImg, dithering, strength):
	img = cv2.cvtColor(input, cv2.COLOR_BGR2RGB)
	img = Image.fromarray(img).convert("RGB")

	dithering += 1

	if palImg is not None:
		palImg = cv2.cvtColor(palImg, cv2.COLOR_BGR2RGB)
		palImg = Image.fromarray(palImg).convert("RGB")
		numColors = len(palImg.getcolors(16777216))
	else:
		numColors = colors

	palette = []

	threshold = (16*strength)/4

	if palImg is not None:

		numColors = len(palImg.getcolors(16777216))

		if strength > 0:
			img = adjust_gamma(img, 1.0-(0.02*strength))
			for i in palImg.getcolors(16777216):
				palette.append(i[1])
			palette = hitherdither.palette.Palette(palette)
			img_indexed = hitherdither.ordered.bayer.bayer_dithering(img, palette, [threshold, threshold, threshold], order=2**dithering).convert('RGB')
		else:
			for i in palImg.getcolors(16777216):
				palette.append(i[1][0])
				palette.append(i[1][1])
				palette.append(i[1][2])
			palImg = Image.new('P', (256, 1))
			palImg.putpalette(palette)
			img_indexed = img.quantize(method=1, kmeans=numColors, palette=palImg, dither=0).convert('RGB')
	elif colors > 0:

		if strength > 0:
			img_indexed = img.quantize(colors=colors, method=1, kmeans=colors, dither=0).convert('RGB')
			img = adjust_gamma(img, 1.0-(0.03*strength))
			for i in img_indexed.convert("RGB").getcolors(16777216):
				palette.append(i[1])
			palette = hitherdither.palette.Palette(palette)
			img_indexed = hitherdither.ordered.bayer.bayer_dithering(img, palette, [threshold, threshold, threshold], order=2**dithering).convert('RGB')

		else:
			img_indexed = img.quantize(colors=colors, method=1, kmeans=colors, dither=0).convert('RGB')

	result = cv2.cvtColor(np.asarray(img_indexed), cv2.COLOR_RGB2BGR)
	return result

def run_palettize(processed, downscale, original, upscale, kcentroid, scale, paletteDropdown, paletteURL, palette, clusters, dither, ditherStrength):
	if ditherStrength > 0:
		print(f'Palettizing output to {clusters} colors with order {2**(dither+1)} dithering...')
	else:
		print(f'Palettizing output to {clusters} colors...')

	if paletteDropdown != "None" and paletteDropdown != "Automatic":
		palette = cv2.cvtColor(cv2.imread(pal_path+paletteDropdown), cv2.COLOR_RGB2BGR)

	if paletteURL != "":
		try:
			palette = np.array(Image.open(BytesIO(requests.get(paletteURL).content)).convert("RGB")).astype(np.uint8)
		except:
			print("An error occured fetching image from URL")

	# TODO: support batch of images
	#generations = p.batch_size*p.n_iter
	generations = 1

	originalImgs = []

	for i in range(generations):
		# Converts image from "Image" type to numpy array for cv2

		img = np.array(processed.images[i]).astype(np.uint8)

		if original:
			originalImgs.append(processed.images[i])

		if downscale:
			if kcentroid:
				img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert("RGB")
				img = cv2.cvtColor(np.asarray(kCentroid(img, int(img.width/scale), int(img.height/scale), 2)), cv2.COLOR_RGB2BGR)
			else:
				img = cv2.resize(img, (int(img.shape[1]/scale), int(img.shape[0]/scale)), interpolation = cv2.INTER_LINEAR)

		if paletteDropdown == "Automatic":
			palImg = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert("RGB")
			best_k = determine_best_k(palImg, 64)
			palette = cv2.cvtColor(np.asarray(palImg.quantize(colors=best_k, method=1, kmeans=best_k, dither=0).convert('RGB')), cv2.COLOR_RGB2BGR)

		tempImg = palettize(img, clusters, palette, dither, ditherStrength)

		if downscale:
			img = cv2.resize(tempImg, (int(img.shape[1]*scale), int(img.shape[0]*scale)), interpolation = cv2.INTER_NEAREST)

		if upscale:
			tempImg = img

		#processed.images[i] = Image.fromarray(img)
		# Save the downscaled image
		processed.images[i] = Image.fromarray(tempImg)

	if original:
		processed.images.extend(originalImgs)

	return processed
