import os
import argparse
import multiprocessing
import sys

import cv2


REQUIRED_RES = 1280, 720
SATURATION_COEF = 1.2


def read_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--videos", required=True, type=str,
                        help="Path to a video(s) to crop")
    parser.add_argument("-s", "--save_path", default="", type=str,
                        help="Path where results will be saved")
    return vars(parser.parse_args())


def process_video(args: dict) -> None:
    pid = os.getpid()
    print(f"[INFO]: Process {pid} started. Got video {args['video']}")

    sections_to_crop = args["time_sections"]
    if not len(sections_to_crop):
        print(f"[WARNING]: Process {pid} didn't get any "
              f"time sections to slice")
        sys.exit()

    path_to_video = args["video"]
    cap = cv2.VideoCapture(path_to_video)
    assert cap.isOpened(), f"[ERROR]: Process {pid} " \
                           f"failed to open {path_to_video}"
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    msg = f"[ERROR]: Wrong video resolution! Expected: {REQUIRED_RES}"
    assert frame_w == REQUIRED_RES[0] and frame_h == REQUIRED_RES[1], msg
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    video_name = os.path.splitext(os.path.basename(path_to_video))[0]
    video_writer = None
    frames_passed, seconds_passed = 0, 0
    tracking_ad = sections_to_crop.pop(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        frames_passed += 1
        if frames_passed == fps:
            seconds_passed += 1
            if seconds_passed % 100 == 0 and seconds_passed != 0:
                print(f"[INFO]: Process {pid} processed "
                      f"{seconds_passed} seconds")
            frames_passed = 0

        start, end = tracking_ad
        if seconds_passed == start:
            if video_writer is None:
                save_path = os.path.join(
                    args["save_path"], f"{video_name}_{start}_{end}.avi"
                )
                video_writer = cv2.VideoWriter(
                    save_path, fourcc, fps, (frame_w, frame_h), True
                )
        elif seconds_passed >= end and video_writer is not None:
            video_writer = None
            try:
                tracking_ad = sections_to_crop.pop(0)
            except Exception:
                break

        if video_writer:
            video_writer.write(frame)

    cv2.destroyAllWindows()
    cap.release()
    print(f"[INFO]: Process {pid} done")


def main() -> None:
    args = read_args()
    if not os.path.exists(args["save_path"]):
        os.mkdir(args["save_path"])
    # Sadly time sections to slice out need to be
    # checked and written below manually
    sections_to_crop = {
        "2.flv": [
            (6 * 60 + 45, 23 * 60 + 47),
            (26 * 60 + 57, 36 * 60 + 7),
            (39 * 60 + 12, 59 * 60 + 59),
        ],
        "3.flv": [
            (4 * 60 + 6, 17 * 60 + 52),
            (22 * 60 + 6, 32 * 60 + 40),
            (36 * 60 + 40, 47 * 60 + 6),
            (50 * 60 + 45, 59 * 60 + 59),
        ],
        "4.flv": [
            (1 * 60 + 23, 9 * 60 + 57),
            (12 * 60 + 55, 50 * 60 + 41),
            (54 * 60 + 52, 59 * 60 + 59),
        ],
        "7.flv": [
            (0 * 60 + 1, 8 * 60 + 0),
            (11 * 60 + 55, 22 * 60 + 41),
            (27 * 60 + 43, 36 * 60 + 19),
            (40 * 60 + 43, 45 * 60 + 57),
            (50 * 60 + 15, 63 * 60 + 19),
        ],
        "8.flv": [
            (2 * 60 + 30, 8 * 60 + 25),
            (13 * 60 + 2, 31 * 60 + 13),
            (35 * 60 + 30, 43 * 60 + 19),
            (48 * 60 + 43, 56 * 60 + 6),
            (50 * 60 + 15, 63 * 60 + 19),
        ],
        "9.flv": [
            (0 * 60 + 1, 7 * 60 + 25),
            (10 * 60 + 54, 39 * 60 + 30),
            (42 * 60 + 30, 47 * 60 + 25),
            (50 * 60 + 50, 59 * 60 + 6),
        ],
        "10.flv": [
            (4 * 60 + 52, 12 * 60 + 45),
            (40 * 60 + 54, 48 * 60 + 50),
            (53 * 60 + 1, 62 * 60 + 25),
        ],
        "15.flv": [
            (0 * 60 + 1, 17 * 60 + 0),
            (20 * 60 + 7, 28 * 60 + 31),
            (31 * 60 + 42, 39 * 60 + 32),
            (43 * 60 + 15, 50 * 60 + 56),
        ],
        "16.flv": [
            (4 * 60 + 20, 11 * 60 + 0),
            (15 * 60 + 16, 28 * 60 + 31),
            (31 * 60 + 42, 58 * 60 + 32),
        ],
        "17.flv": [
            (5 * 60 + 30, 25 * 60 + 0),
            (29 * 60 + 16, 35 * 60 + 31),
            (40 * 60 + 30, 59 * 60 + 59),
        ],
        "18.flv": [
            (1 * 60 + 40, 12 * 60 + 0),
            (14 * 60 + 0, 23 * 60 + 21),
            (28 * 60 + 50, 34 * 60 + 20),
            (37 * 60 + 50, 44 * 60 + 40),
        ],
        "19.flv": [
            (3 * 60 + 40, 12 * 60 + 55),
            (16 * 60 + 40, 32 * 60 + 40),
            (36 * 60 + 50, 50 * 60 + 20),
            (37 * 60 + 50, 44 * 60 + 40),
        ]
    }
    jobs = []
    for video_name in os.listdir(args["videos"]):
        video_time_sections = sections_to_crop.get(video_name, None)
        if video_time_sections is None:
            print("[WARNING]: no time sections for video:", video_name)
            continue
        jobs.append({
            "video": os.path.join(args["videos"], video_name),
            "time_sections": video_time_sections,
            "save_path": args["save_path"]
        })
    cores = multiprocessing.cpu_count()
    workers = int(cores * SATURATION_COEF)
    if workers > len(jobs):
        workers = len(jobs)

    print(f"[INFO]: Spawning {workers} workers...")
    with multiprocessing.Pool(workers) as p:
        p.map(process_video, jobs)
    print("[INFO]: Done")


if __name__ == "__main__":
    main()
