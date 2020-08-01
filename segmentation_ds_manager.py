from typing import List, Tuple
import os
import cv2
import argparse
import numpy as np


ALLOWED_EXTS = [".jpg", "jpeg", ".png"]


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder_images", type=str, help="Path to folder with images")
    parser.add_argument("--folder_masks", type=str, default=None, help="Path to folder with corresponding masks")
    parser.add_argument("--save_path", type=str, help="Path to where processed images/masks will be saved")
    parser.add_argument("--slice_img_mask", type=int, help="Slice images and corresponding masks in half")
    parser.add_argument("--overlay_masks", type=int, help="Overlay binary masks over images")
    arguments = parser.parse_args()

    return arguments


def slice_image_mask(
        names: List[str],
        folder_images: str,
        folder_masks: str,
        save_path: str,
        size_thresh: Tuple[int, int] = (1000, 1000)
) -> None:
    if not os.path.exists(os.path.join(save_path, "cropped_images")):
        os.mkdir(os.path.join(save_path, "cropped_images"))
    if not os.path.exists(os.path.join(save_path, "cropped_masks")):
        os.mkdir(os.path.join(save_path, "cropped_masks"))

    def cut_in_two(image: np.ndarray, mask: np.ndarray) -> List[list]:
        height, width = image.shape[:2]
        if height > width:
            half_height = height // 2
            image_top = image[:half_height, :, :]
            image_bot = image[half_height + 1:, :, :]
            mask_top = mask[:half_height, :, :]
            mask_bot = mask[half_height + 1:, :, :]
            return [[image_top, mask_top], [image_bot, mask_bot]]
        else:
            half_width = width // 2
            image_left = image[:, :half_width, :]
            image_right = image[:, half_width + 1:, :]
            mask_left = mask[:, :half_width, :]
            mask_right = mask[:, half_width + 1:, :]
            return [[image_left, mask_left], [image_right, mask_right]]

    for name in names:
        path_to_image = os.path.join(folder_images, name)
        path_to_mask = os.path.join(folder_masks, name)
        image = cv2.imread(path_to_image)
        if image is None:
            print("Failed to open image named:", name)
            continue
        mask = cv2.imread(path_to_mask)
        if mask is None:
            print("Failed to open mask named:", mask)
            continue

        if not image.shape[:2] == mask.shape[:2]:
            print(f"ATTENTION: Image and mask named {name} sizes do not match. Skipped")
            continue

        if image.shape[0] > size_thresh[0] or image.shape[1] > size_thresh[1]:
            crops = cut_in_two(image, mask)
            for i, crop in enumerate(crops):
                image_, mask_ = crop
                assert image_.shape[:2] == mask_.shape[:2]
                try:
                    cv2.imwrite(os.path.join(save_path, "cropped_images", f"{os.path.splitext(name)[0]}_{i}.png"), image_)
                    cv2.imwrite(os.path.join(save_path, "cropped_masks", f"{os.path.splitext(name)[0]}_{i}.png"), mask_)
                except Exception as e:
                    print(f"Failed while saving cropped image/mask named: {name}. Error: {e}")
                    continue
            print("Sliced", name)

    return


def overlay_masks(names: List[str], folder_images: str, folder_masks: str) -> None:
    for name in names:
        path_to_image = os.path.join(folder_images, name)
        path_to_mask = os.path.join(folder_masks, name)
        image = cv2.imread(path_to_image)
        if image is None:
            print("Failed to open image named:", name)
            continue
        mask = cv2.imread(path_to_mask)
        if mask is None:
            print("Failed to open mask named:", mask)
            continue

        if not image.shape[:2] == mask.shape[:2]:
            print(f"ATTENTION: Image and mask named {name} sizes do not match. Skipped")
            continue

        combined = cv2.addWeighted(image, 0.99, mask, 0.3, 0)

        # Not quite what I want. Check https://stackoverflow.com/questions/44535068/opencv-python-cover-a-colored-mask-over-a-image
        #combined = cv2.bitwise_and(image, cv2.bitwise_not(mask))

        cv2.imshow("", combined)
        cv2.waitKey(0)
        print("Processed", name)

    return


def get_file_names(path_to_folder: str) -> List[str]:
    return [item for item in os.listdir(path_to_folder) if os.path.splitext(item)[-1].lower() in ALLOWED_EXTS]


def main():
    args = parse_arguments()
    if args.save_path and not os.path.exists(args.save_path):
        os.mkdir(args.save_path)

    if args.slice_img_mask and args.folder_images and args.folder_masks:
        image_names = get_file_names(args.folder_images)
        mask_names = get_file_names(args.folder_masks)
        msg = "ERROR: Images do no match the corresponding masks"
        assert set([os.path.splitext(image)[0] for image in image_names]) ==\
                                                        set([os.path.splitext(mask)[0] for mask in mask_names]), msg
        slice_image_mask(image_names, args.folder_images, args.folder_masks, args.save_path)
        return

    elif args.overlay_masks and args.folder_images and args.folder_masks:
        image_names = get_file_names(args.folder_images)
        mask_names = get_file_names(args.folder_masks)
        msg = "ERROR: Images do no match the corresponding masks"
        assert set([os.path.splitext(image)[0] for image in image_names]) == \
                                                        set([os.path.splitext(mask)[0] for mask in mask_names]), msg
        overlay_masks(image_names, args.folder_images, args.folder_masks)
        return

if __name__ == "__main__":
    main()
