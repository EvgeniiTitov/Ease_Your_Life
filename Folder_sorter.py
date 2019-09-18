import cv2
import sys
import numpy as np
import os
import argparse

parser = argparse.ArgumentParser(description = "Folder parser")
parser.add_argument('--folder', help="Path to folder where to take images from")
parser.add_argument('--classes', nargs='+', help="Classes that we want to use images for")
parser.add_argument('--save_path', nargs='+', help="Path where to save an image for each class")
arguments = parser.parse_args()

def relocate_image(path_to_image, class_path, window_name):
    image = cv2.imread(path_to_image)
    image_name = os.path.basename(path_to_image)

    flag = False
    while not flag:
        cv2.imshow(window_name, image)
        key = cv2.waitKey(0)
        for button, element in class_path.keys():
            if key == ord(str(button)):
                print("You've pressed:", key)
                new_path = class_path[(button,element)]
                print("Image will be saved to:", new_path)
                # Save image. Check if its already been saved so you dont create duplicates
                # use new name when saving


            elif key == ord('q'):
                return

def main():

    if not arguments.folder:
        print("No folder has been provided. Giving up")
        sys.exit()
    if not os.path.isdir(arguments.folder):
        print("The folder provided is not a folder! Try again")
        sys.exit()
    path_to_folder = arguments.folder

    if not arguments.classes:
        print("No classes have been provided. Giving up")
        sys.exit()
    classes = []
    for index, element in enumerate(arguments.classes, start=1):
        print("Press", index, "to save images for class", element)
        classes.append((index,element))

    if not arguments.save_path:
        print("No paths where to save images have been provided. Giving up")
        sys.exit()
    save_paths = [_ for _ in arguments.save_path]

    # Zip together (button to press,class( and a path where to save it
    if not len(classes) == len(save_paths):
        print("Number of paths does not correspond to the number of classes provided!")
        sys.exit()

    class_path = dict(zip(classes, save_paths))  # {(1, 'pole'): 'D:\\Desktop\\Test_Dir1', (2, 'isolator'): 'D:\\Desktop\\Test_Dir2', (3, 'dumper'): 'D:\\Desktop\\Test_Dir3'}

    window_name = "Sorting images for datasets"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    for image in os.listdir(path_to_folder):
        path_to_image = os.path.join(path_to_folder, image)
        relocate_image(path_to_image, class_path, window_name)

    print("All images have been processed!")
    sys.exit()

if __name__ == '__main__':
    main()