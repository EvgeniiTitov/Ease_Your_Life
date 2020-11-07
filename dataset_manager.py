import os
import sys
import argparse
import random
import time

import cv2


ALLOWED_EXTS = [".jpg", ".png", ".jpeg"]


def parse_arguments():
    parser = argparse.ArgumentParser(description="Dataset manipulations")
    parser.add_argument("-f", '--folder', nargs="+",
                        help="Path to a folder(s) with images to get modified")
    parser.add_argument("-i", '--image', help="Path to an image to get modified")
    parser.add_argument('--save_path', default=r"D:\Desktop\DSmanager_modified",
                        help="Path where to save modified images")
    parser.add_argument('--ext', help="Changes extension to .jpg")
    parser.add_argument('--split', type=float,
                        help="Split a folder of images into training and valid portions")
    parser.add_argument('--name', help="Renames images in ascending order")
    parser.add_argument('--remove_lowres',
                        help="Removes all images with resolution lower than the threshold")
    parser.add_argument('--new_size', help="Bring all images to the same size")
    parser.add_argument('--fix_russian',
                        help='Remove russian letters from names')
    arguments = parser.parse_args()

    return arguments


class DatasetManager:
    @staticmethod
    def modify_images(
            images,
            modifications,
            save_path
    ) -> None:
        for index, path_to_image in enumerate(images, start=8093):
            image_name = os.path.basename(path_to_image)
            image = cv2.imread(path_to_image)
            if image is None:
                print("Failed to open image:", image_name)
                continue

            # Remove low-res images
            if modifications.remove_lowres:
                min_resolution = int(modifications.remove_lowres)
                try:
                    if image.shape[0] * image.shape[1] < min_resolution:
                        # REMOVE AT SOURCE FOLDER OR COMMENT TO JUST SKIP
                        os.remove(path_to_image)
                        continue
                except:
                    print("Failed to remove:", path_to_image)

            # Change name
            if modifications.name:
                image_name = "{:05}".format(index) + os.path.splitext(path_to_image)[-1]

            # Change extension
            if modifications.ext:
                img_name, extension = os.path.splitext(image_name)
                if not extension.lower() == ".jpg":
                    image_name = img_name + ".jpg"

            # Bring images to the same size
            if modifications.new_size:
                width = height = int(modifications.new_size)
                try:
                    image = cv2.resize(image, (height, width))
                except:
                    print("Failed to resize:", path_to_image)

            # Replace russian letters
            if modifications.fix_russian and modifications.name:
                pass

            elif modifications.fix_russian:
                russian_letters_space = {
                    "а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и",
                    "й", "к", "л", "м", "н", "о", "п", "р", "с", "т",
                    "у", "ф", "х", "ц", "ч", "ш", "щ", "ь", "э", "ю", "я", " "
                }
                rus_letters_found = russian_letters_space & set(image_name)
                if len(rus_letters_found) > 0:
                    image_name = "{:05}".format(index) + '.jpg'

            try:
                cv2.imwrite(os.path.join(save_path, image_name), image)
            except Exception as e:
                print(f"Failed while saving: {image_name}. Error: {e}")
                continue

        print("All images processed")

    @staticmethod
    def split_into_training_valid(
            paths: list,
            destination: str,
            proportion: float
    ) -> None:
        nb_images_to_relocate = int(len(paths) * proportion)
        for i in range(nb_images_to_relocate):
            image_name = os.path.split(paths[i])[-1]
            os.rename(paths[i], os.path.join(destination, image_name))

        print(f"Moved {int(proportion * 100)}% of images to {destination}")


def collect_images(folders: list, container: list) -> list:
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.splitext(file)[-1].lower() in ALLOWED_EXTS:
                container.append(file_path)
            else:
                if os.path.isdir(file_path):
                    collect_images([file_path], container)

    return container


def main():
    arguments = parse_arguments()
    images_to_modify = list()
    start = time.time()

    if arguments.folder:
        # Multiple folders provided. Collect paths to all images to process.
        if len(arguments.folder) > 1:
            print("More than 1 folder provided")
            images_to_modify = collect_images(
                arguments.folder,
                images_to_modify
            )
        elif len(arguments.folder) == 1:
            if not os.path.isdir(arguments.folder[0]):  # nargs return a list
                print(f"{arguments.folder[0]} is not a folder.")
                sys.exit()
            images_to_modify = collect_images(
                arguments.folder,
                images_to_modify
            )
        if not images_to_modify:
            print("No images found")
            sys.exit()
        print(f"{len(images_to_modify)} images collected in"
              f" {time.time() - start} seconds")

    elif arguments.image:
        if not os.path.isfile(arguments.image):
            print("You haven't provided an image")
            sys.exit()
        images_to_modify.append(arguments.image)

    else:
        print("No source of images provided")
        sys.exit()

    if not arguments.save_path:
        print("Default save path will be used")
    else:
        if not os.path.exists(arguments.save_path):
            os.mkdir(arguments.save_path)
    save_path = arguments.save_path

    # Shuffle images so that images of different classes spread evenly
    if len(images_to_modify) > 1:
        random.shuffle(images_to_modify)

    if arguments.split:
        assert 0.0 < arguments.split <= 1.0, "Wrong split value"
        DatasetManager().split_into_training_valid(
            paths=images_to_modify,
            destination=save_path,
            proportion=arguments.split
        )
        return

    DatasetManager().modify_images(
        images=images_to_modify,
        modifications=arguments,
        save_path=save_path
    )


if __name__ == "__main__":
    main()
