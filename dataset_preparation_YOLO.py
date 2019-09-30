# python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\dataset_preparation_YOLO.py --folder=D:\Desktop\testing_directory --remove_lowres=1000 --name=1 --ext=1
# Could possibly add resize function
import os
import cv2
import sys
import argparse

parser = argparse.ArgumentParser(description = "Dataset manipulations")
parser.add_argument('--folder', help="Path to a folder with images to get modified")
parser.add_argument('--image', help="Path to an image to get modified")
parser.add_argument('--save_path', help="Path where to save modified images")
parser.add_argument('--ext', help="Changes extension to .jpg")
parser.add_argument('--name', help="Renames images in ascending order")
parser.add_argument('--remove_lowres', help="Removes all images with resolution lower than the threshold")
parser.add_argument('--YOLO', help="Relative path. Creates txt doc for YOLO with paths to images relative to the main build exe file")
arguments = parser.parse_args()

def relative_path_YOLO():
    pass

def perform_modifications(images, save_path):
    min_resolution = int(arguments.remove_lowres)
    counter = 1
    for path_to_image in images:
        image = cv2.imread(path_to_image)
        # Remove low resolution images
        if arguments.remove_lowres:
            if image.shape[0]*image.shape[1] < min_resolution:
                os.remove(path_to_image)
                continue
        image_name = os.path.basename(path_to_image)
        # Change name
        if arguments.name:
            image_name = '{:05}'.format(counter) + os.path.splitext(path_to_image)[-1]
            #print(image_name)
        # Change extension
        if arguments.ext:
            if not os.path.splitext(path_to_image)[-1] in [".jpg",".JPG"]:
                img_name = image_name[:-4]  # exclude old extension
                image_name = img_name + '.jpg'
                print(image_name)
        # Save modified image
        cv2.imwrite(os.path.join(save_path, image_name), image)
        counter += 1

def main():
    images_to_modify = list()
    if arguments.folder:
        if not os.path.isdir(arguments.folder):
            print("What you've provided is not a folder")
            sys.exit()
        images_to_modify = [os.path.join(arguments.folder, image) for image in os.listdir(arguments.folder)\
                                                            if any(image.endswith(ext) for ext in [".jpg",".JPG",".png",".PNG"])]
        if not images_to_modify:
            print("The folder provided doesn't contain any images. Double check!")
            sys.exit()
    elif arguments.image:
        images_to_modify.append(arguments.image)
    else:
        print("You haven't provided a single source of images")
        sys.exit()

    save_path = arguments.save_path if arguments.save_path else arguments.folder  # By default images get saved back to the source folder
    perform_modifications(images_to_modify, save_path)

    # YOLO relative path

if __name__=="__main__":
    main()