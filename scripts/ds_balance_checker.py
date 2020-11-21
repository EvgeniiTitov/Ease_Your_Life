import os
import argparse
from typing import Tuple


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", type=str, required=True,
                        help="Path to a dataset folder")
    return vars(parser.parse_args())


def collect_txts(txts: list, dir_path: str) -> list:
    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        if filename.endswith(".txt"):
            txts.append(filepath)
        elif os.path.isdir(filepath):
            collect_txts(txts, filepath)

    return txts


def collect_txts_gen(dir_path: str) -> str:
    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        if filename.endswith(".txt"):
            yield filepath
        elif os.path.isdir(filepath):
            yield from collect_txts_gen(filepath)


def read_txt_content(txt_path: str) -> Tuple[list, bool]:
    content = []
    try:
        with open(txt_path, "r") as f:
            for line in f:
                content.append(line.split(" "))
        return content, True
    except:
        return content, False


def main():
    args = read_args()
    if not os.path.exists(args["folder"]):
        raise Exception("Provided folder doesn't exist")

    labels = dict()
    for txt in collect_txts_gen(args["folder"]):
        content, read = read_txt_content(txt)
        if not read:
            print(f"Failed to read {os.path.basename(txt)}'s content")
            continue
        for label in content:
            cls, *coords = label
            if cls not in labels.keys():
                labels[cls] = 0
            labels[cls] += 1

    print("\nDataset classes distribution:")
    for key in sorted(labels.keys()):
        print(f"Class: {key}. Number of objects: {labels[key]}")


if __name__ == "__main__":
    main()
