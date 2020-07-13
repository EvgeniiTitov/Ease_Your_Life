from typing import List, Tuple
import numpy as np
import os
import sys
import cv2


ALLOWED_EXTS = ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"]


def collect_paths(path_to_data: str, img_paths: List[str], txt_paths: List[str]) -> Tuple[list, list]:
    for item in os.listdir(path_to_data):
        path_to_item = os.path.join(path_to_data, item)

        if os.path.isfile(path_to_item):
            if any(item.endswith(ext) for ext in ALLOWED_EXTS):
                img_paths.append(path_to_item)
            elif item.endswith("txt"):
                txt_paths.append(path_to_item)
        elif os.path.isdir(path_to_item):
            collect_paths(path_to_item, img_paths, txt_paths)
        else:
            continue

    return img_paths, txt_paths


def get_txt_content(path_to_txt: str, class_to_search: int) -> List[list]:
    assert os.path.isfile(path_to_txt), "Something went wrong"
    obj_coordinates = list()
    try:
        with open(path_to_txt, mode="r") as file:
            for line in file:
                elements = line.split()
                if elements[0] == str(class_to_search):
                    obj_coordinates.append(
                        [float(elements[1]), float(elements[2]), float(elements[3]), float(elements[4])]
                    )
    except Exception as e:
        print(f"Failed while reading txt: {path_to_txt}. Error: {e}")
        return list()

    return obj_coordinates


def slice_np_array_using_coordinates(image: np.ndarray, coordinates: List[list]) -> List[np.ndarray]:
    sliced_out_imgs = list()
    h, w = image.shape[0:2]
    for coordinate in coordinates:
        centre_x = int(coordinate[0] * w)
        centre_y = int(coordinate[1] * h)
        width = int(coordinate[2] * w)
        height = int(coordinate[3] * h)

        left = int(centre_x - width / 2)
        top = int(centre_y - height / 2)
        right = int(left + width)
        bot = int(top + height)
        assert all((left < right, top < bot)), "b0ss, I have a problem"

        try:
            subimage = np.array(image[top:bot, left:right, :])
        except Exception as e:
            print(f"Failed while slicing out a bb numpy array. Error: {e}")
            continue
        sliced_out_imgs.append(subimage)

    return sliced_out_imgs


def save_cropped_images(images: List[np.ndarray], save_path: str, image_name: str) -> None:
    for i, image in enumerate(images):
        path_to_save = os.path.join(save_path, f"{image_name}_{i}.jpg")
        try:
            cv2.imwrite(path_to_save, image)
        except Exception as e:
            print(f"Failed while saving image: {image_name}. Error: {e}")
            continue

    return

def process_images_and_txts(path_to_images: List[str], path_to_txts: List[str], save_path: str, cls: int) -> None:
    for path_to_image, path_to_txt in zip(path_to_images, path_to_txts):
        if os.path.splitext(os.path.basename(path_to_image))[0] != os.path.splitext(os.path.basename(path_to_txt))[0]:
            print("Names do not match. Skipped")
            continue

        try:
            image = cv2.imread(path_to_image)
        except Exception as e:
            print(f"Failed to open an image: {path_to_image}. Error: {e}")
            continue

        coordinates = get_txt_content(path_to_txt, cls)
        if not coordinates:
            continue

        cropped_images = slice_np_array_using_coordinates(image, coordinates)
        save_cropped_images(cropped_images, save_path, image_name=os.path.splitext(os.path.basename(path_to_image))[0])


def main():
    path_to_data = r"D:\Desktop\Reserve_NNs\Datasets\DATASETS_FOR_TEACHING\components\components_1-2573"
    save_path = r"D:\Desktop\Reserve_NNs\Datasets\raw_data\DEFECTS\dumpers\Cropped\cropped_from_firstLabelling"
    class_to_crop_out = 1  # dumpers index during image labelling

    # Collect paths to images and corresponding txts with labels
    img_paths, txt_paths = list(), list()
    img_paths, txt_paths = collect_paths(path_to_data, img_paths, txt_paths)

    # Make sure items are sorted based on their name (number from 1 - N)
    img_paths.sort(key=lambda path: os.path.splitext(os.path.basename(path))[0])
    txt_paths.sort(key=lambda path: os.path.splitext(os.path.basename(path))[0])

    process_images_and_txts(img_paths, txt_paths, save_path, class_to_crop_out)

if __name__ == "__main__":
    main()