import argparse
import os
from typing import List

from pytube import YouTube


def read_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--urls", nargs="+", required=True, help="Path to video(s) to download"
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default=r"D:\SingleView\SpotIQ\tests\BATCH3\test_videos",
        help="Path where results will be saved",
    )
    return vars(parser.parse_args())


def download_videos(links: List[str], save_path: str) -> None:
    for link in links:
        try:
            downloader = YouTube(url=link)
        except Exception as e:
            print(
                f"Failed to instantiate YouTube class for the link: {link}. "
                f"Error: {e}"
            )
            continue

        print("\nAvailable video resolutions for downloading are:")
        for stream in downloader.streams:
            print(stream)
        input_ = input("\nSELECT TAG TO DOWNLOAD:")

        try:
            input_ = int(input_)
        except Exception as e:
            print(f"Failed to convert user input to int. Int expected. " f"Error: {e}")
            continue

        try:
            print("Downloading")
            downloader.streams.get_by_itag(input_).download(save_path)
        except Exception as e:
            print(f"Failed during video downloading. Error: {e}")
            continue


def main():
    # Parse args
    args = read_args()
    print("SAVE PATH:", args["save_path"])
    if not os.path.exists(args["save_path"]):
        try:
            os.mkdir(args["save_path"])
        except Exception as e:
            print(
                f"Failed while creating a directory to save downloaded videos. "
                f"Error: {e}"
            )
            raise e

    download_videos(args["urls"], args["save_path"])


if __name__ == "__main__":
    main()
