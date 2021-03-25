import os
import argparse
import multiprocessing

import cv2


ALLOWED_EXTS = ['.mp4', '.avi', '.flv']
SKIP_FRAMES = 1
SATURATION_COEF = 1.5


'''
.read() is blocking - is must be calling the C API.
'''



def read_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder',
                        help='Path to a folder containing videos.')
    parser.add_argument('-v', '--video', help='Path to a video file.')
    parser.add_argument('--frame', type=int, default=25,
                        help='Save a frame once in N frames.')
    parser.add_argument('-s', '--save_path', required=True,
                        help='Path to the dir where cropped frames get saved')
    return vars(parser.parse_args())


def crop_frames(args: dict) -> None:
    pid = os.getpid()
    video_path = args['path_to_video']
    if args["is_multiprocessing"]:
        print(f"Process {pid} started to process {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        if args["is_multiprocessing"]:
            print(f"Process {pid} failed to open video {video_path}")
        else:
            print("Failed to open video:", video_path)
        return
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    output_name = os.path.splitext(os.path.basename(video_path))[0]
    frame_counter = 0
    while True:
        has_frame, frame = cap.read()
        if not has_frame:
            break
        if frame_counter < SKIP_FRAMES:
            frame_counter += 1
            continue
        if frame_counter % args["every_nth"] == 0:
            cv2.imwrite(
                os.path.join(
                    args["save_path"], f"{output_name}_{frame_counter}.jpg"
                ),
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), 100]
            )
        if frame_counter % 1000 == 0 and frame_counter != 0:
            if args["is_multiprocessing"]:
                print(f"Process {pid} processed {frame_counter}/{frame_count}")
            else:
                print(f"Processed {frame_counter}/{frame_count}")
        frame_counter += 1
    if args["is_multiprocessing"]:
        print(f"Process {pid} done")


def main():
    args = read_args()
    save_path = args["save_path"]
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    every_nth_frame = int(args["frame"])
    assert every_nth_frame > 0
    arguments = {
        "path_to_video": str,
        "save_path": save_path,
        "every_nth": every_nth_frame,
        "is_multiprocessing": bool
    }
    if args["video"]:
        if not os.path.splitext(args["video"])[-1].lower() in ALLOWED_EXTS:
            raise Exception("The provided extension is not supported")
        arguments_copy = arguments.copy()
        arguments_copy["path_to_video"] = args["video"]
        arguments_copy["is_multiprocessing"] = False
        crop_frames(arguments_copy)

    elif args["folder"]:
        jobs = []
        for item in os.listdir(args["folder"]):
            if not os.path.splitext(item)[-1].lower() in ALLOWED_EXTS:
                print(f"Cannot process file {item}. Incorrect extension")
                continue
            arguments_copy = arguments.copy()
            arguments_copy["path_to_video"] = os.path.join(
                args["folder"], item
            )
            arguments_copy["is_multiprocessing"] = True
            jobs.append(arguments_copy)
        assert len(jobs), "No videos awaiting processing"
        cores = multiprocessing.cpu_count()
        workers_count = int(cores * SATURATION_COEF)
        if workers_count > len(jobs):
            workers_count = len(jobs)
        print(f"Spawning {workers_count} workers...")
        with multiprocessing.Pool(workers_count) as p:
            p.map(crop_frames, jobs)
        print("Done")


if __name__ == '__main__':
    main()
