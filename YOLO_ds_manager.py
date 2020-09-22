import os
import sys

import cv2
import argparse
import random
from collections import defaultdict


parser = argparse.ArgumentParser(description = "Dataset manipulations")
parser.add_argument("-f", '--folder', nargs="+",
                    help="Path to a folder with images to get modified")
parser.add_argument("-i", '--image', help="Path to an image to get modified")
parser.add_argument('--save_path', help="Path where to save modified images")
parser.add_argument('--ext', help="Changes extension to .jpg")
parser.add_argument('--name', help="Renames images in ascending order")
parser.add_argument('--remove_lowres',
                    help="Removes all images with resolution lower than the threshold")
parser.add_argument('--fix', help='Fix the naming issue')
parser.add_argument('--remove_class',
                    help="Remove class from txt documents to avoid doing it by hand / relabelling data")
parser.add_argument('--fix_indexes',
                    help="Fix indexes from 1-2 to 0-1 for YOLO")
parser.add_argument('--rename_img_txt',
                    help="Rename both images and txt from a certain number, add to the end of already existing dataset")
parser.add_argument('--check_balance',
                    help="Check number of images of each class in the dataset")
parser.add_argument('--downsample', type=int, default=0,
                    help="Downsample an image (larger side) to standard 1920/1080 size keeping aspect ratio")
arguments = parser.parse_args()


DOWNSAMPLE_SIZE = [1080, 1920]
ALLOWED_EXTS = [".jpg", ".png", ".jpeg"]


def generate_empty_txt(folder_with_image: str, save_path: str) -> None:
    for item in os.listdir(folder_with_image):
        path_to_item = os.path.join(folder_with_image, item)
        if not os.path.isfile(path_to_item):
            continue
        item_name = os.path.splitext(item)[0]
        txt_file_name = os.path.join(save_path, item_name + ".txt")
        with open(txt_file_name, "w") as _:
            pass

    return


def check_dataset_balance(
        path_to_folder: str,
        classes: defaultdict
) -> defaultdict:
    assert isinstance(classes, defaultdict), "Wrong dictionary type!"

    for item in os.listdir(path_to_folder):
        path_to_item = os.path.join(path_to_folder, item)

        if os.path.isdir(path_to_item):
            check_dataset_balance(path_to_item, classes)
        elif item.endswith(".txt"):
            with open(path_to_item, mode="r") as file:
                for line in file:
                    elements = line.split()
                    if not elements:
                        continue
                    if elements[0] == "0":
                        classes["countdown"] += 1
                    elif elements[0] == "1":
                        classes["new_world"] += 1
                    elif elements[0] == "2":
                        classes["paknsave"] += 1

    return classes


def get_images_names(path: str) -> list:
    names = []
    for element in os.listdir(path):
        if element.endswith('.txt'):
            continue
        names.append(element)

    return names


def generate_paths_YOLO():
    import random

    #relative_path = r'data/dasha_training/'
    relative_path = '../dataset/images/train/'
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
            if relative_path:
                f.write(os.path.join(relative_path, image) + '\n')
            else:
                f.write(image + "\n")

    print("Done")


def rename_ImgTxt(
        folders: list,
        save_path: str,
        start_index: int = 100_000
) -> None:
    start = start_index
    def rename_txts(txts_to_rename: list, start: int) -> None:
        for txt in txts_to_rename:
            new_txt_name = '{:05}'.format(start) + ".txt"
            os.rename(txt, os.path.join(os.path.split(txt)[0], new_txt_name))
            start += 1
        return

    for folder in folders:
        txts_to_rename = list()

        for filename in os.listdir(folder):
            if filename.endswith('.txt'):
                txts_to_rename.append(os.path.join(folder, filename))
                continue

            if not os.path.splitext(filename)[-1].lower() in ALLOWED_EXTS:
                continue

            path_to_img = os.path.join(folder, filename)
            new_img_name = '{:07}'.format(start_index) + os.path.splitext(filename)[-1]
            try:
                os.rename(path_to_img, os.path.join(folder, new_img_name))
            except Exception as e:
                print(f"Failed to rename: {path_to_img}. Error: {e}. Skipped")
                continue
            start_index += 1

        rename_txts(txts_to_rename, start)

    return


def relocate_img_txt(folders: list, save_path: str, start: int = 3200) -> None:
    for folder in folders:
        # Collect all images and txts to relocate
        paths_to_images = list()
        paths_to_txts = list()
        for filename in os.listdir(folder):
            if filename.endswith("txt"):
                paths_to_txts.append(os.path.join(folder, filename))
            elif any(filename.endswith(ext) for ext in [".jpg", ".JPG", ".png", ".PNG", "jpeg", "JPEG"]):
                paths_to_images.append(os.path.join(folder, filename))
            else:
                continue

        assert len(paths_to_images) == len(paths_to_txts), "Number of images and txts with labels do not match"

        # Relocate image-txt pairs to a new folder with new names
        while paths_to_images:
            path_to_image = paths_to_images.pop(0)
            path_to_txt = paths_to_txts.pop(0)
            assert os.path.splitext(os.path.basename(path_to_image))[0] ==\
                                            os.path.splitext(os.path.basename(path_to_txt))[0], "Something went wrong"

            new_img_name = '{:05}'.format(start) + os.path.splitext(path_to_image)[-1]
            new_txt_name = '{:05}'.format(start) + ".txt"
            try:
                os.rename(path_to_image, os.path.join(save_path, new_img_name))
                os.rename(path_to_txt, os.path.join(save_path, new_txt_name))
            except Exception as e:
                print(f"Failed while renaming: {path_to_image} and {path_to_txt}. Error: {e}. Skipped")
                continue
            start += 1

    return


def rename_txts(path_to_folder: str, save_path: str, start: int = 0) -> None:
    for filename in os.listdir(path_to_folder):
        if not filename.endswith("txt"):
            continue
        path_to_txt = os.path.join(path_to_folder, filename)
        new_name = '{:05}'.format(start) + ".txt"

    return


def replace_rus_letters(images) -> None:
    rus_letters = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и",
                   "й", "к", "л", "м", "н", "о", "п", "р", "с", "т",
                   "у", "ф", "х", "ц", "ч", "ш", "щ", "ь", "э", "ю", "я", " "}

    images_to_rename = [
        path for path in images if len(rus_letters & set(path)) > 0
    ]
    print(f"Found {len(images_to_rename)} images with russian letters in them")
    for image in images_to_rename:
        path_to_folder = os.path.split(image)[0]
        os.rename(
            image,
            os.path.join(path_to_folder, str(random.randint(1, 10**6)) +'.jpg')
        )

    return


def change_class_value(folders) -> None:
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

    return


def remove_class(folders) -> None:
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

    return


def perform_modifications(images: list, save_path: str) -> None:
    if arguments.remove_lowres:
        min_resolution = int(arguments.remove_lowres)

    for index, path_to_image in enumerate(images, start=100_000):
        image = cv2.imread(path_to_image)
        if image is None:
            print("Failed to open:", path_to_image)
            continue

        # Remove low resolution images (with russian letters in the name!)
        if arguments.remove_lowres:
            try:  # Can crash on some images
                if image.shape[0] * image.shape[1] < min_resolution:
                    os.remove(path_to_image)
                    continue
            except:
                print("Failed to delete image:", path_to_image)
                continue

        if arguments.downsample and image.shape[0] > 1920 or image.shape[1] > 1920:
            h, w = image.shape[:2]
            if h > w:
                resize_factor = float(DOWNSAMPLE_SIZE[1] / h)
                new_width = int(w * resize_factor)
                new_height = DOWNSAMPLE_SIZE[1]
            else:
                resize_factor = float(DOWNSAMPLE_SIZE[1] / w)
                new_height = int(h * resize_factor)
                new_width = DOWNSAMPLE_SIZE[1]
            try:
                image = cv2.resize(image, dsize=(new_width, new_height))
            except Exception as e:
                print(f"Failed to downsample the image: {path_to_image} to new size: {(new_width, new_height)}. "
                      f"Error: {e}")
                continue

        image_name = os.path.basename(path_to_image)
        # Change name
        if arguments.name:
            image_name = '{:05}'.format(index) + os.path.splitext(path_to_image)[-1]

        # Change extension
        if arguments.ext:
            if not os.path.splitext(path_to_image)[-1].lower()  == ".jpg":
                img_name = os.path.splitext(image_name)[0]
                image_name = img_name + '.jpg'

        # Save modified image
        try:
            cv2.imwrite(os.path.join(save_path, image_name), image)
        except Exception as e:
            print(f"Failed to save processed image: {image_name}. Error: {e}.")
            continue

    print("All images have been processed")


def collect_all_images(folder: str, images: list) -> tuple:
    '''
    Recursively collect images in a folder and store them in a list. Return the list then.
    '''
    exception = 0
    for filename in os.listdir(folder):
        filename_path = os.path.join(folder, filename)
        if any(filename.endswith(ext) for ext in [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG"]):
            images.append(filename_path)
        elif os.path.isdir(filename_path):
            try:
                collect_all_images(filename_path, images)
            except:
                exception += 1

    return (images, exception)


def main():
    # generate_empty_txt(
    #     folder_with_image=r"D:\negatives",
    #     save_path=r"D:\negatives"
    # )
    # sys.exit()

    generate_paths_YOLO()
    sys.exit()

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
            #rename_ImgTxt(arguments.folder, arguments.save_path)
            relocate_img_txt(arguments.folder, arguments.save_path)
            sys.exit()

        # Launch DS balance checker and exit
        if arguments.check_balance:
            classes = defaultdict(int)
            check_dataset_balance(path_to_folder=arguments.folder[0], classes=classes)

            print("\nRESULTS:")
            for k, v in classes.items():
                print(f"Class: {k}, images: {v}")

            sys.exit()

        # Option 1: If multiple folders provided - collect all images in them (do not include subfolders etc)
        if len(arguments.folder) > 1:
            for folder in arguments.folder:
                if not os.path.isdir(folder):
                    print(f"\n{folder} is not a folder!")
                    continue
                _, exceptions_ = collect_all_images(folder, images_to_modify)
            print(f"Total of {len(images_to_modify)} images have been detected and will be modified.")

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
