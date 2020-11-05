import os
import argparse

import cv2
from typing import Tuple, Set, Union, List
import numpy as np
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import imgaug


AUGMENT_PIPELINE = imgaug.augmenters.Sequential([
    imgaug.augmenters.Fliplr(p=1.0),
    imgaug.augmenters.Rotate(rotate=(-90, 90))
])


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", required=True,
                        help="Path to a folder with image-txt pairs")
    parser.add_argument("-s", "--save_path", required=True,
                        help="Dir where generated images and txts saved")
    return vars(parser.parse_args())


def get_unique_names(dirpath: str) -> Set[str]:
    return {str(os.path.splitext(file)[0]) for file in os.listdir(dirpath)}


def get_img_txt_pair(filenames: Set[str], folder: str) -> Tuple[str, str]:
    for filename in filenames:
        image_path = os.path.join(folder, filename + ".jpg")
        txt_path = os.path.join(folder, filename + ".txt")
        if os.path.exists(image_path) and os.path.exists(txt_path):
            yield image_path, txt_path


def read_txt_content(txt_path: str) -> Tuple[bool, Union[None, list]]:
    boxes = []
    try:
        with open(txt_path, "r") as text_file:
            for line in text_file:
                items = line.split()
                boxes.append(items)
    except Exception as e:
        print(f"Failed to read txt {txt_path}'s content. Error: {e}")
        return False, boxes

    return True, boxes


def read_image(image_path: str) -> Tuple[bool, Union[None, np.ndarray]]:
    try:
        image = cv2.imread(image_path)
    except Exception as e:
        print(f"Failed to open image: {image_path}. Error: {e}")
        return False, None
    return (True, image) if image is not None else (False, image)


def draw_boxes(image: np.ndarray, boxes: list) -> None:
    for box in boxes:
        if len(box) == 5:
            cls_, left, top, right, bot = box
        else:
            cls_ = None
            left, top, right, bot = box
        cv2.rectangle(image, (left, top), (right, bot), (0, 0, 255), 2)
        cv2.putText(
            image, f"class: {cls_}", (left, top + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2
        )


def convert_darknet_to_human(
        boxes: List[list],
        image: np.ndarray
) -> List[list]:
    image_height, image_width = image.shape[:2]
    boxes_out = []
    for box in boxes:
        cls_ = int(box[0])
        centre_x = int(float(box[1]) * image_width)
        centre_y = int(float(box[2]) * image_height)
        bb_width = int(float(box[3]) * image_width)
        bb_height = int(float(box[4]) * image_height)
        left = centre_x - (bb_width // 2)
        top = centre_y - (bb_height // 2)
        right = left + bb_width
        bot = top + bb_height
        boxes_out.append(
            [cls_, left if left > 0 else 1, top if top > 0 else 1, right, bot]
        )
    return boxes_out


def augment_image(image: np.ndarray, boxes: list) -> Tuple[np.ndarray, list]:
    bbs = BoundingBoxesOnImage(
        [
            BoundingBox(x1=box[1], y1=box[2], x2=box[3], y2=box[4])
            for box in boxes
        ],
        shape=image.shape
    )
    aug_image, aug_boxes = AUGMENT_PIPELINE(image=image, bounding_boxes=bbs)
    aug_coords = [
        [
            box.x1_int if box.x1_int > 0 else 1,
            box.y1_int if box.y1_int > 0 else 1,
            box.x2_int if box.x2_int > 0 else 1,
            box.y2_int if box.y2_int > 0 else 1
        ]
        for box in aug_boxes
    ]
    return aug_image, aug_coords


def main() -> None:
    args = read_args()
    if not os.path.exists(args["save_path"]):
        os.mkdir(args["save_path"])
        print("Dir to store results created:", args["save_path"])
    cv2.namedWindow("", cv2.WINDOW_NORMAL)
    filenames = get_unique_names(args["folder"])
    for img_path, txt_path in get_img_txt_pair(filenames, args["folder"]):
        print("Augmentating image:", os.path.basename(img_path))
        success_img, image = read_image(img_path)
        suceess_txt, coords = read_txt_content(txt_path)
        if not all((success_img, suceess_txt)):
            continue
        coords_human = convert_darknet_to_human(coords, image)

        # draw_boxes(image, coords_human)
        # cv2.imshow("ORIGINAL", image)
        # cv2.waitKey(0)

        aug_image, aug_boxes = augment_image(image, coords_human)

        # print("Aug boxes:", aug_boxes)
        # draw_boxes(aug_image, aug_boxes)
        # cv2.imshow("", aug_image)
        # cv2.waitKey(0)

        # TODO: Save images (run some coordinate check, like that its
        #       area > 1, else its a line and something went wrong


if __name__ == "__main__":
    main()
