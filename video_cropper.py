# Press ESC to continue to the next video in --folder mode.
import os
import argparse

import cv2


ALLOWED_EXTS = ['.mp4', '.avi', '.flv']
SKIP_FRAMES = 1


parser = argparse.ArgumentParser(description='Frame Cropper')
parser.add_argument('--folder', help='Path to a folder containing videos.')
parser.add_argument('--video', help='Path to a video file.')
parser.add_argument('--frame', type=int, default=25,
                    help='Save a frame once in N frames.')
parser.add_argument('--save_path', required=True,
                    help='Path to the folder where to save cropped frames.')
arguments = parser.parse_args()


def crop_frames(
        cap: cv2.VideoCapture,
        save_path: str,
        frame_n: int,
        output_name: str
) -> None:
    print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_counter = 0
    while cv2.waitKey(1) < 0:
        has_frame, frame = cap.read()
        if not has_frame:
            break
        cv2.imshow("", frame)

        # Skip first section of the video
        if frame_counter < SKIP_FRAMES:
            frame_counter += 1
            print(frame_counter)
            continue

        if frame_counter % frame_n == 0:
            try:
                cv2.imwrite(
                    os.path.join(save_path, output_name + '_' + str(frame_counter) + '.jpg'),
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                )
            except Exception as e:
                print(f"Failed while saving a frame. Error: {e}")
                continue

        print(frame_counter)
        frame_counter += 1
    print("Video", output_name, "has been processed.")


def main():
    save_path = arguments.save_path  # Path to save frames cropped
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    once_in_N_frames = int(arguments.frame)
    assert once_in_N_frames > 0

    if arguments.video:
        video_path = arguments.video
        if not os.path.splitext(video_path)[-1].lower() in ALLOWED_EXTS:
            raise Exception("The provided extension is not supported")

        output_name = os.path.basename(video_path)[:-4]
        try:
            cap = cv2.VideoCapture(video_path)
        except Exception as e:
            print(f"Failed while creating the cap object. Error: {e}")
            raise e
        assert cap.isOpened()
        crop_frames(cap, save_path, once_in_N_frames, output_name)

    elif arguments.folder:
        if not os.path.isdir(arguments.folder):
            raise Exception("The provided folder is not a folder")

        for video in os.listdir(arguments.folder):
            if not os.path.splitext(video)[-1].lower() in ALLOWED_EXTS:
                continue

            video_path = os.path.join(arguments.folder, video)
            output_name = video[:-4]
            try:
                cap = cv2.VideoCapture(video_path)
            except Exception as e:
                print(
                    f"Failed to create the cap object for {video}. Error: {e}"
                )
                continue

            if not cap.isOpened():
                print("Failed to open the cap for:", output_name)
                continue
            crop_frames(cap, save_path, int(once_in_N_frames), output_name)

    else:
        print("Incorrect input. Giving up")


if __name__ == '__main__':
    main()
