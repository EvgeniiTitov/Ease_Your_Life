# One folder - python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\dataset_preparation_YOLO.py --folder=D:\Desktop\Test_Dir --save_path=D:\Desktop\save_test --remove_lowres=1000 --name=1 --ext=1
# Multiple folders - python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\dataset_preparation_YOLO.py --folder D:\Desktop\Test_Dir\Modified D:\Desktop\Test_Dir\Detections --save_path=D:\Desktop\save_test --remove_lowres=1000 --name=1 --ext=1

# Could possibly add resize function to bring all images to the same size.
import os
import cv2
import sys
import argparse
import random

parser = argparse.ArgumentParser(description = "Dataset manipulations")
parser.add_argument("-f", '--folder', nargs="+", help="Path to a folder with images to get modified")
parser.add_argument("-i", '--image', help="Path to an image to get modified")
parser.add_argument('--save_path', help="Path where to save modified images")
parser.add_argument('--ext', help="Changes extension to .jpg")
parser.add_argument('--name', help="Renames images in ascending order")
parser.add_argument('--remove_lowres', help="Removes all images with resolution lower than the threshold")
parser.add_argument('--fix', help='Fix the bloody issue')
parser.add_argument('--YOLO', help="Relative path. Creates txt doc for YOLO with paths to images relative to the main build exe file")
arguments = parser.parse_args()

def relative_path_YOLO():
    pass

def fix_naming_issues(images):
    '''
    Some *** named some images in russian, which obviously led to inability to open and read those images.
    Find images containing russian letters, rename them with some random names
    '''
    import random
    letters = ["а","о","и","е","ё","э","ы","у","ю","я","г","в"]
    images_to_rename = [path for path in images if any(letter in path.lower() for letter in letters)]
    print(f"Found {len(images_to_rename)} images with russian letters in them")
    for image in images_to_rename:
        path_to_folder = os.path.split(image)[0]
        os.rename(image, os.path.join(path_to_folder, str(random.randint(1,10**5))+'.jpg'))

def perform_modifications(images, save_path):
    '''
    Perform modifications on images one by one checking what modifications have been requested by a user.
    Save the images modified according to the save path provided.
    '''
    min_resolution = int(arguments.remove_lowres)
    counter = 1
    for path_to_image in images:
        image = cv2.imread(path_to_image)
        # Remove low resolution images (with russian letters in the name!)
        if arguments.remove_lowres:
            try:  # Can crash on some images
                if image.shape[0]*image.shape[1] < min_resolution:
                    os.remove(path_to_image)
                    continue
            except:
                print("Failed on image:", path_to_image)
                continue
        image_name = os.path.basename(path_to_image)
        # Change name
        if arguments.name:
            image_name = '{:05}'.format(counter) + os.path.splitext(path_to_image)[-1]
        # Change extension
        if arguments.ext:
            if not os.path.splitext(path_to_image)[-1] in [".jpg",".JPG"]:
                img_name = image_name[:-4]  # exclude old extension
                image_name = img_name + '.jpg'
        # Save modified image
        cv2.imwrite(os.path.join(save_path, image_name), image)
        counter += 1
    print("All images have been processed")

def collect_all_images(folder, images):
    '''
    Recursively collect images in a folder and store them in a list. Return the list then.
    '''
    exception = 0
    for filename in os.listdir(folder):
        filename_path = os.path.join(folder, filename)
        if any(filename.endswith(ext) for ext in [".jpg",".JPG",".png",".PNG"]):
            images.append(filename_path)
        elif os.path.isdir(filename_path):
            try:
                collect_all_images(filename_path, images)
            except:
                exception += 1
    return (images, exception)

def main():
    images_to_modify = list()
    if arguments.folder:
        # Option 1: If multiple folders provided - collect all images in them (do not include subfolders etc)
        if len(arguments.folder) > 1:
            for folder in arguments.folder:
                if not os.path.isdir(folder):
                    print(f"\n{folder} is not a folder!")
                    continue
                images_to_modify += [os.path.join(folder, image) for image in os.listdir(folder)\
                                                                        if any(image.endswith(ext) for ext in [".jpg",".JPG",".png",".PNG"])]
        # Option 2: If only one folder provided - find all images in it including subfolders etc.
        elif len(arguments.folder) == 1:
            if not os.path.isdir(arguments.folder[0]):  # nargs returns a list
                print("What you've provided is not a folder")
                sys.exit()
            images_to_modify, exceptions = collect_all_images(arguments.folder[0], images_to_modify)
            print(f"All {len(images_to_modify)} images have been collected with {exceptions} exceptions")
        # Check if any images have been collected
        if not images_to_modify:
            print("The folder provided doesn't contain any images. Double check!")
            sys.exit()
    elif arguments.image:
        images_to_modify.append(arguments.image)
        if not arguments.save_path:
            print("You haven't provided a path to save the image modified!")
            sys.exit()
    else:
        print("You haven't provided a single source of images")
        sys.exit()

    if arguments.fix:
        fix_naming_issues(images_to_modify)
        sys.exit()

    if not arguments.save_path:
        print("You haven't provided path to where save image(s) modified")
        sys.exit()
    save_path = arguments.save_path
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    # Shuffle list so that images coming from different classes are shuffled and spread
    random.shuffle(images_to_modify)
    perform_modifications(images_to_modify, save_path)

    # YOLO relative path

if __name__=="__main__":
    main()