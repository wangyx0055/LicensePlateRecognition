#coding=utf-8
import os
import shutil
import cv2.cv as cv

def show_image(window_name, image):
	image = scale_image(image, 0.5)
	cv.NamedWindow(window_name)
	cv.ShowImage(window_name, image)

def scale_image(image, scale):
	new_size = (int(image.width*scale), int(image.height*scale))
	new_image = cv.CreateImage(new_size, image.depth, image.nChannels)
	cv.Resize(image, nChannelsew_image, interpolation=cv.CV_INTER_LINEAR)
	return new_image

def grey_image(image):
	# set channel to be 1 for grey image
	grey = cv.CreateImage((image.width, image.height), image.depth, 1)
	cv.CvtColor(image, grey, cv.CV_BGR2GRAY)
	return grey

def smooth_image(image):
	smooth = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	cv.Smooth(image, smooth, cv.CV_MEDIAN)
	return smooth

def linear_translate(image):
	linear_image = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	minVal, maxVal, minLoc, maxLoc = cv.MinMaxLoc(image)
	scale = 255.0 / (maxVal - minVal)
	shift = - (scale * minVal)
	cv.Scale(image, linear_image, scale, shift)
	return linear_image

def gray_swap(image):
	new_image = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	minVal, maxVal, minLoc, maxLoc = cv.MinMaxLoc(image)
	scale = -1
	shift = 255
	cv.Scale(image, new_image, scale, shift)
	return new_image

def sobel_image(image, x, y):
	sobel_image = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	cv.Sobel(image, sobel_image, x, y)
	return sobel_image

def binary_image(image, min_level, max_level):
	new_image = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	minVal, maxVal, minLoc, maxLoc = cv.MinMaxLoc(image)
	threshold = minVal * min_level + maxVal * max_level
	cv.Threshold(image, new_image, threshold, 255, cv.CV_THRESH_BINARY)
	return new_image

def dilate_image(image, v, h):
	vImage = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	hImage = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	vElement = cv.CreateStructuringElementEx(1, v, 0, v/2, cv.CV_SHAPE_RECT)
	hElement = cv.CreateStructuringElementEx(h, 1, h/2, 0, cv.CV_SHAPE_RECT)
	cv.Dilate(image, vImage, vElement, 1)
	cv.Dilate(vImage, hImage, hElement, 1)
	return hImage

def erode_image(image, v, h):
	vImage = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	hImage = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	vElement = cv.CreateStructuringElementEx(1, v, 0, v/2, cv.CV_SHAPE_RECT)
	hElement = cv.CreateStructuringElementEx(h, 1, h/2, 0, cv.CV_SHAPE_RECT)
	cv.Erode(image, vImage, vElement, 1)
	cv.Erode(vImage, hImage, hElement, 1)
	return hImage

# this function has problem
def medium_image(image, px):
	new_image = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	cv.MedianBlur(image, new_image, px)
	return new_image

def edge_image(image):
	swap_image = gray_swap(image)

	image1 = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	image2 = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)
	image_all = cv.CreateImage((image.width, image.height), image.depth, image.nChannels)

	image_x = sobel_image(image, 1, 0)
	image_y = sobel_image(image, 0, 1)
	cv.Add(image_x, image_y, image1)

	image_x = sobel_image(swap_image, 1, 0)
	image_y = sobel_image(swap_image, 0, 1)
	cv.Add(image_x, image_y, image2)

	cv.Add(image1, image2, image_all)

	return image_all

def rgb_image(image):
	r_image = cv.CreateImage((image.width, image.height), image.depth, 1)
	g_image = cv.CreateImage((image.width, image.height), image.depth, 1)
	b_image = cv.CreateImage((image.width, image.height), image.depth, 1)
	cv.Split(image, r_image, g_image, b_image, None)
	return (r_image, g_image, b_image)

def sub_image(image1, image2):
	new_image = cv.CreateImage((image1.width, image1.height), image1.depth, 1)
	cv.Sub(image1, image2, new_image, None)
	return new_image

def add_image(image1, image2):
	new_image = cv.CreateImage((image1.width, image1.height), image1.depth, 1)
	cv.Add(image1, image2, new_image, None)
	return new_image

def blue_image(image):
	r_image, g_image, b_image = rgb_image(image)
	image_1 = sub_image(r_image, b_image)
	image_2 = sub_image(g_image, b_image)
	image_blue = add_image(image_1, image_2)
	return image_blue

def white_image(image):
	# r_image, g_image, b_image = rgb_image(image)
	image_gray = grey_image(image)
	image_gray = binary_image(image_gray, 0.8, 0.2)
	return image_gray

def adaptive_threshold(image):
	new_image = cv.CreateImage((image.width, image.height), image.depth, 1)
	cv.AdaptiveThreshold(image, new_image, 125, cv.CV_ADAPTIVE_THRESH_MEAN_C, cv.CV_THRESH_BINARY, 7, 10)
	return new_image

def adaptive_white(image):
	image_gray = grey_image(image)
	adaptive_image = adaptive_threshold(image_gray)
	new_image = binary_image(adaptive_image, 0, 0.5)
	return new_image

def same_white_image(image_blue, image_white):
	new_image = cv.CreateImage((image_blue.width, image_blue.height), image_blue.depth, 1)
	same_point_count = 0
	for x in xrange(0, image_blue.width):
		for y in xrange(0, image_blue.height):
			value1 = int(image_blue[y, x])
			value2 = int(image_white[y, x])
			if ((255 == value1) and (255 == value2)):
				new_image[y, x] = 255.0
				same_point_count += 1
			else:
				new_image[y, x] = 0.0
	print same_point_count
	if same_point_count > 1000:
		return new_image
	else:
		return image_blue

def blue_white_edge_image(image):
	# get the blue image
	image_blue = blue_image(image)
	blue_binary = binary_image(image_blue, 0, 0.3)

	# get the white edge
	image_white = white_image(image)
	white_edge = edge_image(image_white)

	# get the same of blue and white edge
	new_image = same_white_image(blue_binary, white_edge)
	return new_image

def horizontal_cut(image, min_value, max_value):
	min_value = (int)(min_value)
	max_value = (int)(max_value)
	new_image = cv.CreateImage((image.width, image.height), image.depth, 1)
	for y in xrange(0, image.height):
		white_count = 0
		for x in xrange(0, image.width):
			new_image[y, x] = 0.0
			value = int(image[y, x])
			if (255 == value):
				white_count += 1
			else:
				if white_count != 0:
					if white_count >= min_value and white_count <= max_value:
						for index in xrange(1, white_count+1):
							x_index = x - index
							new_image[y, x_index] = 255.0
				white_count = 0
			# the end
			if x == image.width - 1:
				if white_count != 0:
					if white_count >= min_value and white_count <= max_value:
						for index in xrange(0, white_count):
							x_index = x - index
							new_image[y, x_index] = 255.0
	return new_image

def vertical_cut(image, min_value, max_value):
	min_value = (int)(min_value)
	max_value = (int)(max_value)
	new_image = cv.CreateImage((image.width, image.height), image.depth, 1)
	for x in xrange(0, image.width):
		white_count = 0
		for y in xrange(0, image.height):
			new_image[y, x] = 0.0
			value = int(image[y, x])
			if (255 == value):
				white_count += 1
			else:
				if white_count != 0:
					if white_count >= min_value and white_count <= max_value:
						for index in xrange(1, white_count+1):
							y_index = y - index
							new_image[y_index, x] = 255.0
				white_count = 0
			# the end
			if x == image.width - 1:
				if white_count != 0:
					if white_count >= min_value and white_count <= max_value:
						for index in xrange(0, white_count):
							y_index = y - index
							new_image[y_index, x] = 255.0
	return new_image

#________________________________________________________________________
# # image path setting
load_dir = "load"
save_dirs = ["blue_white", "blue", "white", "adaptive_white", "dilate", "erode", "vertical_cut_short", "horizontal_cut", "vertical_cut"]

for save_dir in save_dirs:
	save_path = "results/" + save_dir
	if os.path.exists(save_path):
		shutil.rmtree(save_path)
	while os.path.exists(save_path):
		pass
	os.mkdir(save_path)

# locate the plate
for filename in os.listdir(load_dir):
	if filename[0] != ".":
		print filename
		load_path = load_dir + "/" + filename
		save_paths = {}
		for save_dir in save_dirs:
			save_paths[save_dir] = "results/" + save_dir + "/" + filename

		image = cv.LoadImage(load_path)

		# blue
		image_blue = blue_image(image)
		blue_binary = binary_image(image_blue, 0, 0.3)
		blue_binary = dilate_image(blue_binary, 10, 10)
		cv.SaveImage(save_paths["blue"], blue_binary)
		
		# white
		image_white = adaptive_white(image)
		cv.SaveImage(save_paths["adaptive_white"], image_white)

		# white edge
		white_edge = edge_image(image_white)
		cv.SaveImage(save_paths["white"], white_edge)

		# get the same of blue and white edge
		same_image = same_white_image(blue_binary, white_edge)
		cv.SaveImage(save_paths["blue_white"], same_image)

		nV = 30
		nH = 80
		tmp_image = dilate_image(same_image, nV, nH)
		cv.SaveImage(save_paths["dilate"], tmp_image)
		
		tmp_image = erode_image(tmp_image, nV, nH)
		cv.SaveImage(save_paths["erode"], tmp_image)

		# n < Y < *
		tmp_image = vertical_cut(tmp_image, 1 * nV, 10000)
		cv.SaveImage(save_paths["vertical_cut_short"], tmp_image)

		# 2n < X < 12n
		tmp_image = horizontal_cut(tmp_image, 2 * nH, 12 * nH)
		cv.SaveImage(save_paths["horizontal_cut"], tmp_image)

		# n < Y < 10n
		tmp_image = vertical_cut(tmp_image, 1 * nV, 10 * nV)
		cv.SaveImage(save_paths["vertical_cut"], tmp_image)

		


# cv.EqualizeHist(image, image_1)

# cv.Smooth(image, tmp, cv.CV_GAUSSIAN, 5, 5)
# cv.AddWeighted(image, 1.5, tmp, -0.5, 0, image)