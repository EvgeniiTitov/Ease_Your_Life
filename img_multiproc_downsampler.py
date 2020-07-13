import multiprocessing
from typing import List
import cv2
import os
import time


class DownSamples:
    allowed_ext = [".jpg", ".jpeg", ".png"]

    @staticmethod
    def split_paths_among_cores(paths_to_images: list, nb_of_cpu_cores: int) -> List[list]:
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
            split.append(path_to_image)

            if len(split) >= images_per_split:
                splits.append(split)
                split = list()

        if split:
            splits[-1].extend(split)
        assert len(splits) == nb_of_cpu_cores, "Eugene, error here"

        return splits

    @staticmethod
    def collect_image_paths(folder: str, paths: list) -> list:
        """

        :param folder:
        :return:
        """
        # NOTE - we're sending a pointer to the list to the recursive calls -> all can update it
        for item in os.listdir(folder):
            path_to_item = os.path.join(folder, item)
            if os.path.isdir(path_to_item):
                DownSamples.collect_image_paths(path_to_item, paths)
            if any(item.endswith(ext.lower()) for ext in DownSamples.allowed_ext):
                paths.append(path_to_item)

        return paths

    @staticmethod
    def downsample_images(path_to_images, save_path, height = 1080):
        """
        :param images:
        :return:
        """
        for path_to_image in path_to_images:
            try:
                # open image
                image = cv2.imread(path_to_image)
                image_name = os.path.basename(path_to_image)

                # downsample image
                (h, w) = image.shape[:2]
                r = height / float(h)
                dim = (int(w * r), height)
                resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

                # save resized image
                path_to_save = os.path.join(save_path, image_name)
                cv2.imwrite(path_to_save, resized)

            except:
                continue


def main():
    NEW_HEIGHT = 200
    path_to_folder = r"D:\Desktop\Reserve_NNs\Datasets\random_images\DOWNSAMPLED_RENAMED"
    save_path = r"D:\Desktop\Reserve_NNs\Datasets\random_images\DOWNSAMPLED_SMALL"
    paths_to_images = list()
    nb_of_cores = multiprocessing.cpu_count()

    # Collect all paths to images to process
    DownSamples.collect_image_paths(path_to_folder, paths_to_images)

    # Split images equally between cores
    splits = DownSamples.split_paths_among_cores(paths_to_images, nb_of_cores)
    assert len(splits) == nb_of_cores, "Nb of cores != nb of splits"

    # Run your processes

    processes = list()
    s = time.time()
    for i in range(nb_of_cores):
        process = multiprocessing.Process(
            target=DownSamples.downsample_images,
            args=[splits[i], save_path, NEW_HEIGHT]
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
