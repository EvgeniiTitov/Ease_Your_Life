import multiprocessing
from img_multiproc_downsampler import DownSamples
from typing import List
import cv2
import os
import time
import shutil
import sys


class Renamer:
    counter = 8093  # new name starts from: counter + '.jpg'

    @staticmethod
    def split_paths_among_cores_and_generate_new_names(paths_to_images: list, nb_of_cpu_cores: int) -> List[List[tuple]]:
        """

        :param paths_to_images:
        :param nb_of_cpu_cores:
        :return:
        """
        images_per_split = len(paths_to_images) // nb_of_cpu_cores
        splits = list()
        split = list()

        while paths_to_images:
            path_to_image = paths_to_images.pop()
            split.append((Renamer.counter, path_to_image))
            Renamer.counter += 1

            if len(split) >= images_per_split:
                splits.append(split)
                split = list()

        if split:
            splits[-1].extend(split)
        assert len(splits) == nb_of_cpu_cores, "Eugene, error here"

        return splits

    @staticmethod
    def rename_images(name_and_path_to_images, save_path):
        """
        :return:
        """
        for name, path_to_image in name_and_path_to_images:
            try:
                new_name = os.path.join(save_path, str(name) + ".jpg")
                # Rename
                #os.rename(path_to_image, new_name)
                # Copy
                shutil.copy(path_to_image, new_name)
            except:
                continue


def main():
    path_to_folder = r"D:\Desktop\Reserve_NNs\Datasets\random_images\DOWNSAMPLED_RENAMED"
    save_path = r"D:\Desktop\Reserve_NNs\Datasets\random_images\yolo"
    paths_to_images = list()
    nb_of_cores = multiprocessing.cpu_count()

    # Collect all paths to images to process
    DownSamples.collect_image_paths(path_to_folder, paths_to_images)

    # Split images equally between cores
    splits = Renamer.split_paths_among_cores_and_generate_new_names(paths_to_images, nb_of_cores)
    assert len(splits) == nb_of_cores, "Nb of cores != nb of splits"

    processes = list()
    s = time.time()
    for i in range(nb_of_cores):
        process = multiprocessing.Process(
            target=Renamer.rename_images,
            args=[splits[i], save_path]
        )
        process.start()
        processes.append(process)
        print(f"Process {process.pid} started")

    for process in processes:
        process.join()

    print(f"All processes successfully joined. Finished in: {round(time.time() - s)} seconds")
    print("All images have been downsampled and saved to:", save_path)


if __name__ == "__main__":
    main()
