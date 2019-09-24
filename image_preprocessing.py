# python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\image_preprocessing.py --image=D:\Desktop\Test_Dir\228.jpg --save_path=D:\Desktop\Test_Dir\Modified --filter=1 --resize=1500,1000

# Allow a user to specify the figure size (kernel size). Set the default one to be something. Make it a global variable
# Canny Edge Detection - https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_canny/py_canny.html
# Consider template matching for isolator rotation?

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
#parser.add_argument()
arguments = parser.parse_args()


def grayscale(image):
    """Converts image to grayscale. Returns the image converted"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def binary():
    pass

def unsharp():
    pass

def mean(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # Convert to HSV. OpenCV opens in BGR
    figure_size = 9
    new_img = cv2.blur(img, (figure_size, figure_size))
    new_img = cv2.cvtColor(new_img, cv2.COLOR_HSV2BGR)
    return new_img

def gaussian(image):
    figure_size = 9
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    new_img = cv2.GaussianBlur(img, (figure_size, figure_size), 0)
    new_img = cv2.cvtColor(new_img, cv2.COLOR_HSV2BGR)
    return new_img

def median(image):
    figure_size = 9
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    new_img = cv2.medianBlur(img, figure_size)
    new_img = cv2.cvtColor(new_img, cv2.COLOR_HSV2BGR)
    return new_img

def conservative():
    pass

def laplacian():
    pass

def crimmins():
    pass

def initialize_modifications(save_path, images, new_size, modifications):
    available_functions = [binary, unsharp, mean, gaussian,
                           median, conservative, laplacian, crimmins, grayscale]

    for image_path in images:
        image = cv2.imread(image_path)
        if new_size:
            image = cv2.resize(image, new_size)
        if modifications:
            for function in available_functions:
                if function.__name__ in modifications:  # get function's name
                    image = function(image)
        #cv2.imshow(window_name, image)
        #cv2.waitKey(0)
        name = os.path.basename(image_path)
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
        modifications = [mod.lower().strip() for mod in input("Modifications: Grayscale, Binary, Unsharp, Mean, Gaussian, Median, Conservative, Laplacian, Crimmins: ").split()]

    #window_name = "window_name"
    #cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    if img_to_process:
        initialize_modifications(save_path, img_to_process, new_size, modifications)
    else:
        print("No images for modification have been found. Check your folder")
        sys.exit()

    print("Done!")

if __name__ == "__main__":
    main()