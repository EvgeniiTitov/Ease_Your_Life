import os
import argparse
import cProfile
import pstats
import io

import cv2
from typing import Tuple, Set, Union, List
import numpy as np
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import imgaug


AUGMENT_PIPELINE = imgaug.augmenters.Sequential([
    imgaug.augmenters.Fliplr(p=1.0),
    imgaug.augmenters.Affine(
        scale=(0.7, 1.3), rotate=(-90, 90), translate_percent={"x": 0.1}
    ),
    imgaug.augmenters.color.ChangeColorTemperature(kelvin=(3500, 12000))
], random_order=True)


def profile(fnc):
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval
    return inner


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", required=True,
                        help="Path to a folder with image-txt pairs")
    parser.add_argument("-s", "--save_path", required=True,
                        help="Dir where generated images and txts saved")
    parser.add_argument("--n", type=int, default=1,
                        help="Number of new augmented images per original")
    return vars(parser.parse_args())


def get_unique_names(dirpath: str) -> Set[str]:
    return {str(os.path.splitext(file)[0]) for file in os.listdir(dirpath)}


def get_img_txt_pair(filenames: Set[str], folder: str) -> Tuple[str, str]:
    for filename in filenames:
        image_path = os.path.join(folder, filename + ".jpg")
        txt_path = os.path.join(folder, filename + ".txt")
        if os.path.exists(image_path) and os.path.exists(txt_path):
            yield image_path, txt_path
        else:
            print("[INFO]: Not complete pair for:", filename)


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


def convert_human_to_darknet(boxes: List[list], img: np.ndarray) -> List[list]:
    img_h, img_w = img.shape[:2]
    out = []
    for box in boxes:
        cls_, left, top, right, bot = box
        box_centre_x = round(((left + right) // 2) / img_w, 6)
        box_centre_y = round(((top + bot) // 2) / img_h, 6)
        width = round((right - left) / img_w, 6)
        height = round((bot - top) / img_h, 6)
        assert all(
            (0.0 <= _ <= 1.0
             for _ in (box_centre_x, box_centre_y, width, height))
        ), "[ERROR]: darknet-style coordinates are not in [0.0, 1.0]"
        out.append([cls_, box_centre_x, box_centre_y, width, height])
    return out


def augment_image(
        image: np.ndarray,
        boxes: list,
        n_of_new_imgs: int,
        max_tries: int = 10,
        visibility_thresh: float = 0.4
) -> Tuple[list, list]:
    assert max_tries > 0
    aug_images, aug_coords = [], []
    generated, tries = 0, 0
    while generated < n_of_new_imgs:
        bbs = BoundingBoxesOnImage(
            [
                BoundingBox(x1=box[1], y1=box[2], x2=box[3],
                            y2=box[4], label=box[0])
                for box in boxes
            ],
            shape=image.shape
        )
        aug_image, aug_boxes = AUGMENT_PIPELINE(image=image,
                                                bounding_boxes=bbs)
        aug_coord = []
        for aug_box in aug_boxes:
            # Check if image happens to be completely out after augmentation
            if not aug_box.is_partly_within_image(aug_image):
                continue
            box_area_total = aug_box.area
            # Click out any bb sections that are beyond the image
            aug_box = aug_box.clip_out_of_image(aug_image)
            box_area_visible = aug_box.area
            # If only a small part of bb is visible, skip this bb
            if box_area_visible / box_area_total < visibility_thresh:
                continue
            aug_coord.append([
                aug_box.label, aug_box.x1_int, aug_box.y1_int,
                aug_box.x2_int, aug_box.y2_int
            ])

        if len(aug_coord):
            aug_images.append(aug_image)
            aug_coords.append(aug_coord)
            generated += 1
        else:
            if tries == max_tries:
                print(f"Failed to generate a valid image in {tries} attempts")
                generated += 1
            else:
                tries += 1

    return aug_images, aug_coords


#@profile
def main() -> None:
    args = read_args()
    if not os.path.exists(args["save_path"]):
        os.mkdir(args["save_path"])
        print("Dir to store results created:", args["save_path"])
    #cv2.namedWindow("", cv2.WINDOW_NORMAL)

    filenames = get_unique_names(args["folder"])
    nb_files = len(filenames)
    for i, (img_path, txt_path) in enumerate(
            get_img_txt_pair(filenames, args["folder"])
    ):
        print(f"{i}/{nb_files}. "
              f"Augmenting image: {os.path.basename(img_path)}")
        success_img, image = read_image(img_path)
        suceess_txt, coords = read_txt_content(txt_path)
        if not all((success_img, suceess_txt)):
            continue
        coords_human = convert_darknet_to_human(coords, image)
        # draw_boxes(image, coords_human)
        # cv2.imshow("", image)
        # cv2.waitKey(0)
        # continue
        aug_images, aug_boxes = augment_image(
            image, coords_human, n_of_new_imgs=args["n"]
        )
        former_name = os.path.splitext(os.path.basename(img_path))[0]

        # for image_, boxes in zip(aug_images, aug_boxes):
        #     draw_boxes(image_, boxes)
        #     cv2.imshow("", image_)
        #     cv2.waitKey(0)

        if len(aug_images):
            for j, (image_, boxes) in enumerate(zip(aug_images, aug_boxes)):
                new_name = f"{former_name}_{j}"
                boxes_darknet = convert_human_to_darknet(boxes, image_)
                txt_save_path = os.path.join(
                    args["save_path"], new_name + ".txt"
                )
                try:
                    # Save image
                    cv2.imwrite(
                        os.path.join(args["save_path"], new_name + ".jpg"),
                        image_
                    )
                    # Save txt
                    with open(txt_save_path, "w") as file:
                        for box_darknet in boxes_darknet:
                            file.write(" ".join([str(e) for e in box_darknet]))
                            file.write("\n")
                except Exception as e:
                    print(f"Failed to save augmented pair img-txt. Error: {e}")
                    continue


if __name__ == "__main__":
    main()
