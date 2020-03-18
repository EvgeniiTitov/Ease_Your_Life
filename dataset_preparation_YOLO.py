# One folder - python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\dataset_preparation_YOLO.py --folder=D:\Desktop\Test_Dir --save_path=D:\Desktop\save_test --remove_lowres=1000 --name=1 --ext=1
# Multiple folders - python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\dataset_preparation_YOLO.py --folder D:\Desktop\Test_Dir\Modified D:\Desktop\Test_Dir\Detections --save_path=D:\Desktop\save_test --remove_lowres=250000 --name=1 --ext=1

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
parser.add_argument('--fix', help='Fix the bloody naming issue')
parser.add_argument('--remove_class', help="Remove class from txt documents to avoid doing it by hand / relabelling data")
parser.add_argument('--fix_indexes', help="Fix indexes from 1-2 to 0-1 for YOLO")
parser.add_argument('--rename_img_txt',
                    help="Rename both images and txt from a certain number up to add to the end of already existing dataset")
arguments = parser.parse_args()


def get_images_names(path):
    """
    Collects path to all images to shuffle them afterwards because I am a human and I make mistakes alright
    :param path: folder with images
    :return: list if paths
    """
    container = []
    for element in os.listdir(path):

        if element.endswith('.txt'):
           continue
        container.append(element)

    return container


def generate_paths_YOLO():
    '''
    Fills .txt doc with names of all images to be fed to a NN relative to the darknet.exe
    Enter source - folder with images
    Destination - txt doc where save relative paths
    '''
    import random

    relative_path = r'data/obj/'
    source = input("Enter the source of images: ")
    destination = input("Enter the destination TXT file: ")

    if not os.path.isfile(destination):
        raise TypeError("You haven't specified path to a TXT document")

    shuffle = input("Do you want to have images shuffled? Y/N: ")

    images = get_images_names(source)

    if shuffle.upper().strip() == "Y":
        random.shuffle(images)

    with open(destination, 'w') as f:
        for image in images:
            f.write(os.path.join(relative_path, image) + '\n')

    print("Done")


def rename_ImgTxt(folders,
                  start_index=1):
    """
    Not the most efficient approach, two O(n)s in a sequence. Can we do it in one loop by processing pairs of image-txt
    with the same name?
    """
    start = start_index

    def rename_txts(txts_to_rename, start):

        for txt in txts_to_rename:
            new_txt_name = '{:05}'.format(start) + ".txt"
            os.rename(txt, os.path.join(os.path.split(txt)[0], new_txt_name))
            start += 1

        print("Done")

    for folder in folders:
        txts_to_rename = list()

        for filename in os.listdir(folder):
            # Collect all txts to handle them after the images
            if filename.endswith('.txt'):
                txts_to_rename.append(os.path.join(folder, filename))
                continue
            # Make sure we process only images
            if not any(filename.endswith(ext) for ext in [".jpg", ".JPG", ".png", ".PNG", "jpeg", "JPEG"]):
                continue

            path_to_img = os.path.join(folder, filename)
            new_img_name = '{:05}'.format(start_index) + os.path.splitext(filename)[-1]
            os.rename(path_to_img, os.path.join(folder, new_img_name))
            start_index += 1

        rename_txts(txts_to_rename, start)


def replace_rus_letters(images):
    '''
    Find images containing russian letters, rename them with some random names, will be renamed
    properly later
    '''
    import random

    rus_letters = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и",
                   "й", "к", "л", "м", "н", "о", "п", "р", "с", "т",
                   "у", "ф", "х", "ц", "ч", "ш", "щ", "ь", "э", "ю", "я", " "}


    #images_to_rename = [path for path in images if any(letter in path.lower() for letter in letters)]

    images_to_rename = [path for path in images if len(rus_letters & set(path)) > 0]

    print(f"Found {len(images_to_rename)} images with russian letters in them")

    for image in images_to_rename:
        path_to_folder = os.path.split(image)[0]
        os.rename(image, os.path.join(path_to_folder, str(random.randint(1,10**6))+'.jpg'))

    print("Done")


def change_class_value(folders):
    '''
    To change indexes of the objects getting taught to YOLO from 1-2 to 0-1 since i removed the poles
    '''
    for folder in folders:

        for item in os.listdir(folder):

            if not item.endswith('.txt'):
                continue
            path_to_txt = os.path.join(folder, item)
            path_to_tmp_txt = os.path.join(folder, 'temporary.txt')

            with open(path_to_txt, "r") as data_file, \
                    open(path_to_tmp_txt, "w") as temporary_file:
                for line in data_file:
                    items = line.split()
                    if items[0] == '1':
                        items[0] = '0'
                        temporary_file.write(' '.join(items) + '\n')
                    elif items[0] == '2':
                        items[0] = '1'
                        temporary_file.write(' '.join(items) + '\n')

            os.remove(path_to_txt)
            os.rename(path_to_tmp_txt, path_to_txt)

    print("Fixed")


def remove_class(folders):
    '''
    To save time removes coordinates of BB belonging to a certain class from the txt documents prepared for YOLO training.
    '''
    for folder in folders:

        for item in os.listdir(folder):

            if not item.endswith('.txt'):
                continue

            path_to_txt = os.path.join(folder, item)
            path_to_tmp_txt = os.path.join(folder, 'temporary.txt')

            # Open txt file to read its content, create a temporary txt file to write the content excluding a certain class.
            with open(path_to_txt, "r") as data_file,\
                        open(path_to_tmp_txt, "w") as temporary_file:
                for line in data_file:
                    class_, coordinate1, coordinate2, coordinate3, coordinate4 = line.split()
                    # We want to exclude class 0 - poles, to skip these lines
                    if class_ == '1':
                        continue
                    elif class_ == '2':
                        continue
                    temporary_file.write(line)

            # Replace the original txt file with the new updated one
            os.remove(path_to_txt)
            os.rename(path_to_tmp_txt, path_to_txt)

    print("All txt documents have been processed")


def perform_modifications(images, save_path):
    '''
    Perform modifications on images one by one checking what modifications have been requested by a user.
    Save the images modified according to the save path provided.
    '''
    min_resolution = int(arguments.remove_lowres)

    for index, path_to_image in enumerate(images, start=1):
        image = cv2.imread(path_to_image)

        # Remove low resolution images (with russian letters in the name!)
        if arguments.remove_lowres:
            try:  # Can crash on some images
                if image.shape[0] * image.shape[1] < min_resolution:
                    os.remove(path_to_image)
                    continue
            except:
                print("Failed on image:", path_to_image)
                continue

        image_name = os.path.basename(path_to_image)
        # Change name
        if arguments.name:
            image_name = '{:05}'.format(index) + os.path.splitext(path_to_image)[-1]

        # Change extension
        if arguments.ext:
            if not os.path.splitext(path_to_image)[-1] in [".jpg",".JPG"]:
                img_name = image_name.split(".")[0]  # exclude old extension
                image_name = img_name + '.jpg'

        # Save modified image
        cv2.imwrite(os.path.join(save_path, image_name), image)

    print("All images have been processed")


def collect_all_images(folder, images):
    '''
    Recursively collect images in a folder and store them in a list. Return the list then.
    '''
    exception = 0
    for filename in os.listdir(folder):
        filename_path = os.path.join(folder, filename)

        if any(filename.endswith(ext) for ext in [".jpg", ".JPG", ".png", ".PNG", "jpeg", "JPEG"]):
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
        # Launch removing class function and exit upon completion
        if arguments.remove_class:
            remove_class(arguments.folder)
            sys.exit()

        # Launch fixing indexes problem function and exit on completion
        if arguments.fix_indexes:
            change_class_value(arguments.folder)
            sys.exit()

        # Launch renaming TXTs and IMGs function and exit upon completion
        if arguments.rename_img_txt:
            rename_ImgTxt(arguments.folder)
            sys.exit()

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
            print("The folder(s) provided doesn't contain any images. Double check!")
            sys.exit()

    elif arguments.image:
        images_to_modify.append(arguments.image)

    else:
        print("You haven't provided a single source of images")
        sys.exit()

    # Launch a fixing function and exit upon completion
    if arguments.fix:
        replace_rus_letters(images_to_modify)
        sys.exit()

    # Save path
    if not arguments.save_path:
        print("You haven't provided path to where save image(s) modified")
        sys.exit()
    save_path = arguments.save_path

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    # Shuffle list so that images belonging to different classes are shuffled and spread evenly across dataset
    random.shuffle(images_to_modify)

    perform_modifications(images_to_modify, save_path)

if __name__=="__main__":
    main()
