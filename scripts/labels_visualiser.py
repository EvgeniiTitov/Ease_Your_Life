import argparse
import os
from typing import List
from typing import Tuple

import cv2
import numpy as np


ALLOWED_EXTS = [".jpg", ".JPG", ".png", ".PNG", "jpeg", "JPEG"]


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="Path to a folder with image-txt pairs")

    return parser.parse_args()


def read_txt_content(path_to_txt: str) -> list:
    boxes = list()
    with open(path_to_txt, "r") as text_file:
        for line in text_file:
            items = line.split()
            boxes.append(items)

    return boxes


def draw_bb(image: np.ndarray, bbs: list) -> float:
    image_height, image_width = image.shape[:2]
    ratio = 0.0
    nb_bbs = 0
    print("Image area:", image_height * image_width)
    for i, bb in enumerate(bbs):
        centre_x = int(float(bb[1]) * image_width)
        centre_y = int(float(bb[2]) * image_height)
        bb_width = int(float(bb[3]) * image_width)
        bb_height = int(float(bb[4]) * image_height)

        left = centre_x - (bb_width // 2)
        top = centre_y - (bb_height // 2)
        right = left + bb_width
        bottom = top + bb_height
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

        bb_area = (right - left) * (bottom - top)
        print("Box size:", bb_area)
        ratio += float(bb_area / (image_width * image_height))
        nb_bbs += 1

    return ratio / nb_bbs


def collect_img_txt_pairs(path_to_folder: str) -> Tuple[list, list]:
    path_to_images, path_to_txts = list(), list()
    for filename in os.listdir(path_to_folder):
        if filename.endswith(".txt"):
            path_to_txts.append(os.path.join(path_to_folder, filename))
        elif any(filename.endswith(ext) for ext in ALLOWED_EXTS):
            path_to_images.append(os.path.join(path_to_folder, filename))
        else:
            continue

    assert len(path_to_images) == len(path_to_txts)
    assert set(os.path.splitext(e)[0] for e in path_to_images) == set(
        os.path.splitext(e)[0] for e in path_to_txts
    )

    return path_to_images, path_to_txts


def visualise_images(path_to_images: List[str], path_to_txts: List[str]) -> None:
    cv2.namedWindow("", cv2.WINDOW_NORMAL)
    while path_to_images and path_to_txts:
        path_to_image = path_to_images.pop(0)
        path_to_txt = path_to_txts.pop(0)
        print("Showing:", os.path.basename(path_to_image))

        image = cv2.imread(path_to_image)
        if image is None:
            print("Failed to open image", path_to_image)
            continue

        try:
            bbs = read_txt_content(path_to_txt)
        except Exception:
            print(f"Failed while reading txt content: {path_to_txt}")
            continue

        average_bb_ratio = draw_bb(image, bbs)
        cv2.putText(
            image,
            os.path.basename(path_to_image),
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 0),
            2,
        )
        cv2.putText(
            image,
            f"Ratio: {round(average_bb_ratio, 3)}",
            (50, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 0),
            2,
        )
        cv2.imshow("", image)
        cv2.waitKey(0)

    assert not path_to_images and not path_to_txts, "Didn't process all pairs"
    return


def main():
    args = read_args()
    assert os.path.isdir(args.folder), "Wrong input provided. Folder expected"
    path_to_images, path_to_txts = collect_img_txt_pairs(args.folder)
    visualise_images(path_to_images, path_to_txts)


if __name__ == "__main__":
    main()
