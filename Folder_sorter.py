import cv2
import sys
import os
import argparse
import shutil

parser = argparse.ArgumentParser(description = "Folder parser")
parser.add_argument('--folder', help="Path to folder where to take images from")
parser.add_argument('--classes', nargs='+', help="Classes that we want to split images in")
parser.add_argument('--save_path', nargs='+', help="Path where to save an image for each class")
parser.add_argument('--delete', default=False, help="Delete an image after its been processed")
arguments = parser.parse_args()

def relocate_image(path_to_image, class_path, window_name):
    image_name = os.path.basename(path_to_image)
    try:
        image = cv2.imread(path_to_image, cv2.IMREAD_COLOR)
    except:
        print("Failed to open",image_name)
        return  # Go process the next image

    flag = False
    while not flag:
        cv2.imshow(window_name, image)
        key = cv2.waitKey(0)
        for button, element in class_path.keys():
            # Wait until a key gets pressed. Check if it is the one we track
            if key == ord(str(button)):
                print("You've pressed:", chr(key))
                new_path = class_path[(button,element)]
                print(f"Image {image_name} will be saved to:", new_path)
                shutil.copy(path_to_image, new_path)
            # If Q gets pressed, go process the next image
            elif key == ord('q'):
                if delete:
                    print(f"Image {image_name} has been deleted")
                    os.remove(path_to_image)
                return
            # If ESC gets pressed, remember where stopped, exit
            elif key == 27:
                path = r"C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts"
                with open(os.path.join(path, "last_processed.txt"),"w") as f:
                    f.write(image_name)
                    print("Saved last image processed in text document")
                sys.exit()

def main():
    global delete
    # Check if user wants to have images in source folder deleted after they were processed
    delete = arguments.delete
    # Process the source folder provided
    if not arguments.folder:
        print("No folder has been provided. Giving up")
        sys.exit()
    if not os.path.isdir(arguments.folder):
        print("The folder provided is not actually a folder! Try again!")
        sys.exit()
    path_to_folder = arguments.folder
    # Process classes that a user wants to have images split into
    if not arguments.classes:
        print("No classes have been provided. Giving up")
        sys.exit()
    classes = []
    for index, element in enumerate(arguments.classes, start=1):
        print("Press", index, "to save images for class", element)
        classes.append((index,element))
    # Process paths to which a user wants to save images depending on its class
    if not arguments.save_path:
        print("No paths where to save images have been provided. Giving up")
        sys.exit()
    save_paths = list()
    for path in arguments.save_path:
        if not os.path.exists(path):
            os.mkdir(path)
        save_paths.append(path)
    # Zip together (button to press,class) and a path where to save it
    if not len(classes) == len(save_paths):
        print("Number of save paths does not correspond to the number of classes provided!")
        sys.exit()
    class_save_path = dict(zip(classes, save_paths))  # {(1, 'pole'): 'D:\\Desktop\\Test_Dir1', (2, 'isolator'): 'D:\\Desktop\\Test_Dir2'}
    # Create a window a show images getting processed
    window_name = "Spliting images into different datasets"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # Traverse over all images in the source folder, for each call relocating function
    for filename in os.listdir(path_to_folder):
        if not any(filename.endswith(ext) for ext in [".jpg", ".JPG", ".JPEG", ".jpeg", ".png", ".PNG"]):
            continue
        path_to_image = os.path.join(path_to_folder, filename)
        relocate_image(path_to_image, class_save_path, window_name)
    # Once all images have been processed, exit the script
    print("All images have been processed!")
    sys.exit()

if __name__ == '__main__':
    main()