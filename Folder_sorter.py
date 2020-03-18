# EXAMPLE:
# python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\folder_sorter.py
# --folder=D:\Desktop\testing
# --classes concrete metal
# --save_path D:\Desktop\testing\Concrete D:\Desktop\testing\Metal

# Make sure you provide classes and save paths in order!
import cv2
import sys
import os
import argparse
import shutil

parser = argparse.ArgumentParser(description = "Folder parser")
parser.add_argument('--folder', help="Source folder with images to split")
parser.add_argument('--classes', nargs='+', help="Classes we want to split images in")
parser.add_argument('--save_path', nargs='+', help="Path where to save an image for each class")
parser.add_argument('--delete', type=int, default=0, help="Delete an image after its been processed")
arguments = parser.parse_args()


russian_letters_space = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и",
                         "й", "к", "л", "м", "н", "о", "п", "р", "с", "т",
                         "у", "ф", "х", "ц", "ч", "ш", "щ", "ь", "э", "ю", "я", " "}


def relocate_image(
        path_to_image,
        class_path,
        window_name,
        image_counter
):

    image_name = os.path.basename(path_to_image)
    original_name = image_name

    rus_letters = set(image_name) & russian_letters_space
    if len(rus_letters) > 0:
        image_name = "{:05}".format(image_counter) + '.jpg'
        new_path = os.path.join(os.path.split(path_to_image)[0], image_name)
        os.rename(path_to_image, new_path)
        path_to_image = new_path

    try:
        image = cv2.imread(path_to_image, cv2.IMREAD_COLOR)
    except:
        print("Failed to open: ", original_name)
        return

    if image is None:
        print("Failed to open:", original_name)
        return

    while True:

        cv2.imshow(window_name, image)
        key = cv2.waitKey(0)

        for button, element in class_path.keys():

            # Wait until a key gets pressed. Check if it is the one we track
            if key == ord(str(button)):
                print("You've pressed:", chr(key))

                new_path = class_path[(button, element)]
                print(f"Image {image_name} will be saved to:", new_path)

                shutil.copy(path_to_image, new_path)

            # If Q gets pressed, move on to the next image
            elif key == ord('q'):
                return

            # if D is pressed, delete current image
            elif key == ord('d'):
                if arguments.delete:
                    print(f"Image {image_name} has been deleted")
                    os.remove(path_to_image)

                return

            # If ESC gets pressed, remember where stopped, exit
            elif key == 27:
                sys.exit()


def main():

    # Process the source folder provided
    if not arguments.folder or not os.path.isdir(arguments.folder):
        print("ERROR: Wrong input. Giving up")
        sys.exit()

    source_folder = arguments.folder

    # Process classes that a user wants to have images split into
    if not arguments.classes:
        print("No classes have been provided. Giving up")
        sys.exit()

    classes = list()
    for index, element in enumerate(arguments.classes, start=1):
        print("Press", index, "to save images for class", element)
        classes.append((index, element))

    # Process paths to which a user wants to save images depending on its class
    if not arguments.save_path:
        print("No paths where to save images have been provided. Giving up")
        sys.exit()

    save_paths = list()
    for path in arguments.save_path:

        if not os.path.exists(path):
            os.mkdir(path)
        save_paths.append(path)

    assert len(classes) == len(save_paths), "ERROR: N of paths to save != N of classes"

    # Zip together (button to press, class) and a path where to save it
    # {(1, 'pole'): 'D:\\Desktop\\Test_Dir1', (2, 'isolator'): 'D:\\Desktop\\Test_Dir2'}
    class_save_path = dict(zip(classes, save_paths))

    # Create a window to show images getting processed
    window_name = "Image sorter"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Traverse over all images in the source folder, for each call relocating function
    for index, filename in enumerate(os.listdir(source_folder)):

        if not any(filename.endswith(ext) for ext in [".jpg", ".JPG", ".JPEG", ".jpeg", ".png", ".PNG"]):
            continue

        relocate_image(path_to_image=os.path.join(source_folder, filename),
                       class_path=class_save_path,
                       window_name=window_name,
                       image_counter=index)

    # Once all images have been processed, exit the script
    print("All images have been processed!")


if __name__ == '__main__':
    main()
