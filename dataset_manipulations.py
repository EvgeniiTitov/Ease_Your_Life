'''
1) Given folder with folders inside. Inside each folder there might be some images. Move all those images to one folder changing their names

Add. . Like copy all images from one folder to another one. Might need it for testing purposes on another folder, so we don't harm our
main data. You can ask if user wants to move all images, or like 25%, half etc.

Add. Cut off EXIF data from files. Combine it with some function below. Makes images size smaller, should not cause any issues when working with NN

Improvements:
1) Ask user if he wants to delete folders after everything's been taken from there. Implement delition.
2) Ask if images are in one folder (can be collected recursively) or spread out across the system(provide paths). Implement recursive approach
3) If empty folder was provided? endless try except is no good. Think how you can fix it.
4) When adding images to existing file, they can already start from some index. Ask what index to start with
5) Changing extension function. Can be combined with the main one?

1) Count number of files in a folder plus return list with paths to all elements (file index, extension, path)
2) Change extensions
3) Creating train.txt for YOLOv3.

'''
import os
import PIL
from PIL import Image



def strip_metadata(path_folder, path_save):
    pass


def QuickScriptToFixIssue(source, destination):
    #Not connected from main()
    #To fix issue and find and relocate images that have already got their labels after crash. Took their txt files (1k size, not 0).
    names_to_relocate = []
    exception = 0
    for item in os.listdir(destination):
        names_to_relocate.append(item[:-4])  # to cut extension. get txts numbers.

    for image in os.listdir(source):
        path_to_img = os.path.join(source, image)
        if image[:-4] in names_to_relocate:
            try:
                os.rename(path_to_img, os.path.join(destination, image))
            except:
                exception += 1
        else:
            continue

    print(f'Done with {exception} exception(s)')


def copy_content():
    pass

def initialize_copy_content():
    pass


def move(folders, delete_folder = False):
    """
    (folder to move 1, folder to move 2, ... , destination folder)
    delete. By default False. Deletes folders after images have been taken from there and the folder is empty
    """
    extensions_to_grab = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']  # extensions of files (images) to grab from folders
    folder_to_move = folders[-1] #folder to move all images found to.
    j = 0 #to rename images
    nb_of_files = 0
    for folder in folders[:-1]: #up to the last one
        try: #in case of an empty folder, weird ass file or something.
            for item in os.listdir(folder): #go to each folder, traverse over all elements there
                if any(item.endswith(extension) for extension in extensions_to_grab):
                    path_to_file = os.path.join(folder, item)
                    os.rename(path_to_file, folder_to_move + '//' + '{:05}'.format(j) + os.path.splitext(path_to_file)[-1])
                    j += 1
                    nb_of_files += 1
                else:
                    continue
        except:
            pass
        #Check if folder is empty.
        #Delete it if True. Pass if false.
    print(f'\nDone! {nb_of_files} have been moved. Check the destination folder.')

def initialize_move():
    """
    Ask user for folders whose content he'd like to merge renaming images.
    """
    print("\nWelcome to relocating function. If your images are located within one folder you can provide just path to this folder"
          "If your images are spread out across multiple folders you will have to provide path to each folder. Also, user is to"
          "provide the destination folder - where images will be stored!\n")

    #CHECK IF USER WANTS TO HAVE FOLDERS DELETED
    delete_folder = False
    user_input4 = input("Do you want to have folders deleted after images have been taken from there and the folder is empty?: YES / NO ")
    if user_input4.upper().strip() == "YES":
        delete_folder = True

    #ASK USER TO PROVIDE PATH(S) TO THE FOLDER(S) CONTAINING IMAGES
    folders_to_merge = [] #Container to collect path(s) to folder(s) from which images need to be moved
    i = 0
    user_input0 = input("\nAre your images located in one folder or spread out across several folders? SPREAD \ ONE ")
    if user_input0.upper().strip() == 'SPREAD':
        print("Enter folders from which you'd like to relocate images.")
        print("\nType DONE when done")
        while True:
            user_input = input(f"Provide {i}st/th folder: ")
            if user_input.upper().strip() == "DONE":
                break
            else:
                folders_to_merge.append(user_input)
                i += 1
    elif user_input0.upper().strip() == 'ONE':
        folders_to_merge.append(input("Enter the folder containing all your images: "))
    else:
        print("Wrong input! Try again")
        return

    #ASK USER FOR THE DESTINATION FOLDER - WHERE TO RELOCATE IMAGES
    user_input2 = input("\nEnter the folder to which you'd like to move your files: ")
    if user_input2:
        folders_to_merge.append(user_input2)
    else:
        print("Wrong input. Try again.")
        return

    #ASK USER TO CONFIRM THE DATA PROVIDED IS CORRECT
    print("\nYou've provided the following folders to merge:\n")
    for i in range(len(folders_to_merge) - 1): #last one is the destination folder to move everything to
        print(folders_to_merge[i])

    print("\nThe destination folder:")
    print(folders_to_merge[-1])

    user_input3 = input("\nConfirm this is correct?: YES \ NO ")
    if user_input3.upper().strip() == 'YES':
        print("Calling moving function... Please wait.")
        move(folders_to_merge, delete_folder)
    elif user_input3.upper().strip() == 'NO':
        print("No worries! Please try again.")
        return
    else:
        print("Wrong input! Try again")
        return


def change_extensions(folder, extensions):
    # Fixed. Bag. Must be replacing existing jpg images with newly converted images with the same names.
    # Logic can be done better. Check if extension is already jpg, skip this file. Plus when saving file new file as jpg we can select to keep the old name
    # or renew it!
    from PIL import Image
    i = 0 #to count items found
    exception = 0 #to count exceptions raised
    for item in os.listdir(folder):
        filepath = os.path.join(folder, item)
        if any(item.endswith(ext) for ext in extensions):
            try:
                with Image.open(filepath) as im:  # Makes sense to use with open() so that we don't need to manually close each image
                    im_RGB = im.convert('RGB')
                    im_RGB.save(os.path.join(folder,'{:05}.jpg'.format(i)))
                i += 1
                os.remove(filepath)
            except:
                exception += 1 #counts how many images failed to be reformated
        else:
            os.rename(filepath, os.path.join(folder, '{:05}.jpg'.format(i))) #Renaming existing jpgs to make everything look neat
            i += 1

    print(f"\nDone changing extension.{i} files processed. {exception} exception(s) have been raised during the process.")


def initialize_extension():
    """
    Changes extensions of all images in the folder provided to .jpg
    """
    print("\nHi there. Welcome to the function that changes extensions of images!")
    extensions = ['.png', '.PNG', '.jpeg', '.JPEG']
    source_folder = input("Please provide the folder: ")
    if not os.path.isdir(source_folder):
        print("Wrong input! Try again.")
        return

    change_extensions(source_folder, extensions)



def shuffle_paths_to_images():
    container = []
    source = r'D:\Desktop\darknet-master\build\darknet\x64\data\obj'
    for item in os.listdir(source):
        container.append(item)
    pass


def initialize_yolo():
    '''
    Creates .txt doc with names of all images to be fed to a NN relative to the darknet.exe
    '''
    relative_path = r'data/obj/'
    source = r'D:\Desktop\darknet-master\build\darknet\x64\data\obj'
    destination = r'D:\Desktop\darknet-master\build\darknet\x64\data\train.txt'

    with open(destination, 'w') as f:
        for item in os.listdir(source):
            if item.endswith('.txt'):
                continue
            f.write(os.path.join(relative_path, item) + '\n')

    print("Done my dude!")

def main():
    print("WELCOME TO DATA MANIPULATION SCRIPT GOOD SIR")
    status = True
    while status:
        user_input1 = input("What would you like to do? MOVE / CHANGE EXTENSION / YOLO / EXIT ")
        if user_input1.upper().strip() == 'MOVE':
            initialize_move()
        elif user_input1.upper().strip() == 'CHANGE':
            initialize_extension()
        elif user_input1.upper().strip() == 'YOLO':
            initialize_yolo()
        elif user_input1.upper().strip() == 'EXIT':
            return
        else:
            print("Wrong input. Try again!")

        user_input2 = input("Would you like to perform another operation?: YES / NO ")
        if user_input2.upper().strip() == 'NO':
            status = False
            print("Thank you mate! See you.")

if __name__ == '__main__':
    main()