import cv2
import argparse
import os


'''
COMPLETE ME I AM NOT WORKING
'''


def parse_arguments():
    parser = argparse.ArgumentParser(description="Dataset manipulations")
    parser.add_argument("video", help="path to video to convert")
    parser.add_argument("--output_format", default="mp4", help="Desired output format")
    parser.add_argument("--save_path", default="D:\Desktop\SIngleView", help="Path where converted video will be saved")
    arguments = parser.parse_args()

    return arguments


def convert_video(path_to_video: str, output_format: str, save_path: str) -> bool:
    cap = cv2.VideoCapture(path_to_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_size = (
        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    )
    try:
        video_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, frame_size)
    except Exception as e:
        print(f"Failed while creating video writer. Error: {e}")
        return False

    while True:
        has_frame, frame = cap.read()
        if not has_frame:
            break
        video_writer.write(frame)

    return True


def main():
    args = parse_arguments()

    path_to_video = args.video
    output_format = args.output_format
    save_path = args.save_path
    assert os.path.exists(path_to_video), "The provided path's leading to nothing. Check it"
    assert output_format in ["mp4",], "Cannot convert to the provided output format"
    if not os.path.exists(save_path):
        try:
            os.mkdir(output_format)
        except Exception as e:
            print(f"Failed while creating the destination directory. Error: {e}")
            raise e
    status = convert_video(path_to_video, output_format, save_path)
    if status:
        print("Video has been successfully converted")
    else:
        print("Something went wrong. Video wasn't converted")


if __name__ == "__main__":
    main()
