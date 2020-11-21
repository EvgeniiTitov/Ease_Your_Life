import os
import argparse
import itertools
from typing import Set, List

import numpy as np
import cv2


ALLOWED_EXT = [".jpg", ".png", ".jpeg"]
AVAILABLE_ALGORITHMS = ["dhash", "humming"]


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", nargs="+",
                        help="Path to a folder with images")
    parser.add_argument("--remove", default=0, type=int,
                        help="Remove duplicates or not. Expected 0 or 1")
    parser.add_argument("--algorithm", default="dhash", type=str,
                        help="Available algorithms: dhash, humming")
    parser.add_argument("--humming_thresh", type=float, default=10,
                        help="Humming distance threshold")
    return parser.parse_args()


def calculate_dhash(image: np.ndarray, hash_size: int = 8) -> int:
    """
    Creates a numerical representation of an input image by calculating
    relative horizontal gradient between adjacent pixels and then converting
    it into a hash.
    Images with the same numerical representation are considered duplicates
    :param image:
    :param hash_size:
    :return:
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Convert to gray so no need to compare pixel values across 3 channels
    resized_image = cv2.resize(gray_image, dsize=(hash_size + 1, hash_size))
    difference_image = resized_image[:, 1:] > resized_image[:, :-1]

    return sum([2 ** i for i, v in enumerate(difference_image.flatten()) if v])


def collect_image_paths(folder: str, paths: list) -> list:
    assert os.path.isdir(folder), "Argument folder is not a folder but a file"
    for file in os.listdir(folder):
        path_to_file = os.path.join(folder, file)
        if os.path.splitext(file)[-1].lower() in ALLOWED_EXT:
            paths.append(path_to_file)
        elif os.path.isdir(path_to_file):
            collect_image_paths(path_to_file, paths)

    return paths


def calculate_hamming_distance(hash_1: int, hash_2: int) -> bin:
    return bin(int(hash_1) ^ int(hash_2)).count("1")


def convert_hash(hash_) -> int:
    return int(np.array(hash_, dtype="float64"))


def visualise_similar_images(
        paths: Set[str],
        thumbnail_size: int = 400
) -> None:
    if len(paths) > 4:
        thumbnail_size = 200

    print("\nPATHS OF SIMILAR/IDENTICAL IMAGES:")
    duplicate_images = None
    for path in paths:
        print(path)
        image = cv2.imread(path)
        if image is None:
            print("Failed to open image:", path)
            continue
        image = cv2.resize(image, (thumbnail_size, thumbnail_size))
        # Concat images for visualisation purposes
        if duplicate_images is None:
            duplicate_images = image
        else:
            duplicate_images = np.hstack([duplicate_images, image])
    cv2.imshow("Duplicated images", duplicate_images)
    cv2.waitKey(0)

    return


def generate_hashes_for_images(
        paths_to_images: List[str],
        algorithm: str = "dhash"
) -> dict:
    hashes = dict()
    print("Calculating hashes...")
    for i, path_to_image in enumerate(paths_to_images):
        print(f"Processing: {i} / {len(paths_to_images)}")
        try:
            image = cv2.imread(path_to_image)
        except Exception as e:
            print(
                f"Failed to open: {path_to_image}. Error: {e}. Image skipped"
            )
            continue

        if algorithm == "dhash":
            hash_ = calculate_dhash(image)
        else:
            hash_ = convert_hash(calculate_dhash(image))

        # Get a list of all image paths for the calculated hash if any.
        # Else, returns an empty list
        paths = hashes.get(hash_, list())
        paths.append(path_to_image)
        hashes[hash_] = paths

    return hashes


def run_dhash_algorithm(args, paths_to_images: List[str]) -> None:
    hashes = generate_hashes_for_images(paths_to_images, "dhash")
    # Handle duplicates
    for hash_, paths in hashes.items():
        if not len(paths) > 1:
            continue
        if not args.remove:
            visualise_similar_images(paths)
        else:
            print()
            print(f"Detected {len(paths)} duplicates of {paths[0]}")
            for path in paths[1:]:
                print("Removing duplicates of:", os.path.basename(paths[0]))
                os.remove(path)
    return


def run_humming_algorithm(args, paths_to_images: List[str]) -> None:
    paths_of_similar_images = set()
    hashes = generate_hashes_for_images(paths_to_images, "humming")

    #TODO: Review how you store duplicates. How they are stored together! Wrong
    #      You need to assemble similar images together, so you can delete and leave only 1
    #      Using dict with hashes of similar imgs as keys might work

    for hash_, paths in hashes.items():
        if len(paths) > 1:
            paths_of_similar_images.update(set(paths))

    #Check for similar images: humming distance between
    # hashes within the threshold
    for k1, k2 in itertools.combinations(hashes, 2):
        if calculate_hamming_distance(k1, k2) <= args.humming_thresh:
            paths_of_similar_images.update(set(hashes[k1]))
            paths_of_similar_images.update(set(hashes[k2]))

    if args.remove:
        for path in paths_of_similar_images[1:]:
            os.remove(path)
    else:
        if len(paths_of_similar_images) > 1:
            visualise_similar_images(paths_of_similar_images)
        else:
            print("\nNo similar images to visualise")

    return


def main() -> None:
    args = read_args()
    assert args.humming_thresh >= 0, "Wrong value of hummning distance"
    assert args.algorithm.lower().strip() in AVAILABLE_ALGORITHMS, \
                        "Wrong algorithm requested. Available: dhash, humming"

    image_paths = []
    for folder in args.folder:
        if not os.path.isdir(folder):
            print("Not a folder provided:", folder)
            continue
        paths = collect_image_paths(folder, [])
        print(f"Found {len(paths)} images in the folder {folder}")
        image_paths.extend(paths)
    print("Total images to check:", len(image_paths))

    if args.algorithm.lower().strip() == "dhash":
        run_dhash_algorithm(args, image_paths)
    elif args.algorithm.lower().strip() == "humming":
        run_humming_algorithm(args, image_paths)
    return


if __name__ == "__main__":
    main()
