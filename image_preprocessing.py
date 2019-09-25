# python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\image_preprocessing.py --image=D:\Desktop\Test_Dir\228.jpg --save_path=D:\Desktop\Test_Dir\Modified --filter=1 --resize=1500,1000

# TO ADD:
# Edge detection (Canny) - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_canny/py_canny.html
# 2D Convolution (Custom image filtering) - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
# Image rotation - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html
# ! Contours (Important) - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
# Histograms - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_histograms/py_histogram_equalization/py_histogram_equalization.html
# Hough line for shape detection - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html

import os
import sys
import argparse
import cv2

parser = argparse.ArgumentParser(description="Image modifications")
parser.add_argument("--folder", help="Path to a folder containing images")
parser.add_argument("--image", help="Path to an image")
parser.add_argument("--save_path", help="Path to a folder to save an image processed")
parser.add_argument("--resize", help="Resize image to a new width, height size")
parser.add_argument("--filter", help="Perform some image modifications")
parser.add_argument("--kernel", default=9, help="Kernel size")
arguments = parser.parse_args()

def grayscale(image):
    """Converts image to grayscale. Returns the image converted"""
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

def adaptive(image):
    """Calculates the threshold for a small regions of the image. Give different thresholds for
       different regions of the same image. Hence, better results for images with varying illumination"""
    img = grayscale(image)
    img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    return img

def thresholding(image):
    """Image binarization. Doesn't work well for images with varying illumination"""
    img = grayscale(image)
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return img

def unsharp():
    pass

def bilateral(image):
    """Effective at noise removal while preserving edges. However, its slower compared to other filters, so be careful"""
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    new_image = cv2.bilateralFilter(img,9,75,75)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_HSV2BGR)
    return new_image

def mean(image, kernel_size):
    """Takes the average of all pixels under kernel area and replaces the central element with this average.
       Blurs image to remove noise. Smooths edges of the image."""
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # Convert to HSV. OpenCV opens in BGR
    new_img = cv2.blur(img, (kernel_size, kernel_size))
    new_img = cv2.cvtColor(new_img, cv2.COLOR_HSV2BGR)
    return new_img

def gaussian(image, kernel_size):
    """Similar to mean but it involves a weighted average of the surrounding pixels and it has sigma parameter.
       Gaussian filter blurs the edges but it does a better job of preserving them compared to the mean filter"""
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    new_img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    new_img = cv2.cvtColor(new_img, cv2.COLOR_HSV2BGR)
    return new_img

def median(image, kernel_size):
    """Calculates the median of the pixel intensities that surround the centre pixel in a NxN kernel. The median
    pixel gets replaced with the new value. Does a better job of removing salt-n-pepper noise compared to the mean and
    Gaussian filters. Preserves edges of an image but does not deal with speckle noise."""
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    new_img = cv2.medianBlur(img, kernel_size)
    new_img = cv2.cvtColor(new_img, cv2.COLOR_HSV2BGR)
    return new_img

def conservative():
    pass

def laplacian():
    pass

def crimmins():
    pass

def initialize_modifications(save_path, images, new_size, modifications, kernel_size):
    '''
    :param save_path: path to save image(s) modified to
    :param images:  paths to image(s) to modify
    :param new_size: if specified, the new size to converts image(s) to
    :param modifications: if specified, modifications to perform upon image(s)
    :param kernel_size: if specified, kernel size
    '''
    available_functions = [adaptive, thresholding, unsharp, mean, gaussian,
                           median, bilateral, laplacian, crimmins, grayscale]

    for image_path in images:
        # open an image
        image = cv2.imread(image_path)
        # perform modifications
        if new_size:
            image = cv2.resize(image, new_size)
        if modifications:
            for function in available_functions:
                if function.__name__ in modifications:  # get function's name
                    if function.__name__ in ["bilateral","grayscale","thresholding","adaptive"]:
                        image = function(image)
                    else:
                        image = function(image, kernel_size)

        #cv2.imshow(window_name, image)
        #cv2.waitKey(0)

        # save the image modified. Include modifications performed to the image name
        name = '_'.join(modifications)+'_'+os.path.basename(image_path)
        cv2.imwrite(os.path.join(save_path, name), image)

def main():
    global window_name
    # READ USER INPUT
    if not arguments.save_path:
        print("You have to specify path to a folder where to save an image(s) modified.")
        sys.exit()
    save_path = arguments.save_path # Check if it exists, create it doesnt

    if not any((arguments.folder, arguments.image)):
        print("You haven't given any input image")
        sys.exit()

    img_to_process = list()
    if arguments.image:
        img_to_process.append(arguments.image)

    if arguments.folder:
        if not os.path.isdir(arguments.folder):
            print("What you've provided is not a folder")
            sys.exit()
        # Generate a list of paths to images to process
        img_to_process = [os.path.join(arguments.folder, filename) for filename in os.listdir(arguments.folder)\
                                                    if any(filename.endswith(ext) for ext in [".jpg", ".JPG", ".png", ".PNG"])]
    new_size = tuple()
    if arguments.resize:
        new_size = tuple(int(e) for e in arguments.resize.split(','))  # width, height

    modifications = list()
    if arguments.filter:
        modifications = [mod.lower().strip() for mod in input("Modifications: Grayscale, Thresholding, "
                                                              "Adaptive, Unsharp, Mean, Gaussian, "
                                                              "Median, Bilateral, Laplacian, Crimmins or 0 (to exit): ").split(',')]

    kernel_size = arguments.kernel

    if '0' in modifications:
        sys.exit()

    #window_name = "window_name"
    #cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    if img_to_process:
        initialize_modifications(save_path, img_to_process, new_size, modifications, kernel_size)
    else:
        print("No images for modification have been found. Check your folder")
        sys.exit()

    print("Done!")

if __name__ == "__main__":
    main()