import os

import cv2


def main():
    SAVE_PATH = r"D:\SingleView\SpotIQ\tests\CHANNELS\cropped_ads"
    ad_times = [
        (64*60 + 40, 65*60 + 10),
        # (44*60 + 40, 45*60 + 27),
        # (14*60 + 46, 15*60 + 15),
        # (16 * 60 + 40, 16 * 60 + 52),
        # (52 * 60 + 48, 53 * 60 + 0),
        # (65 * 60 + 59, 66 * 60 + 15)
    ]
    path_to_video = r"D:\SingleView\SpotIQ\tests\nz_tvnz1_2020_07_01_nz_tvnz1-1593641277_nz_tvnz1-1593641277.flv"
    cap = cv2.VideoCapture(path_to_video)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    video_name = os.path.splitext(os.path.basename(path_to_video))[0]
    video_writer = None
    frames_passed, seconds_passed = 0, 0
    tracking_ad = ad_times.pop(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        frames_passed += 1
        if frames_passed == fps:
            seconds_passed += 1
            frames_passed = 0
            print("Seconds passed:", seconds_passed)

        start, end = tracking_ad
        if seconds_passed == start:
            if video_writer is None:
                save_path = os.path.join(
                    SAVE_PATH, f"{video_name}_{start}_{end}.avi"
                )
                video_writer = cv2.VideoWriter(
                    save_path, fourcc, fps, (frame_w, frame_h), True
                )
        elif seconds_passed >= end and video_writer is not None:
            video_writer = None
            try:
                tracking_ad = ad_times.pop(0)
            except:
                break

        if video_writer:
            cv2.imshow("", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            video_writer.write(frame)

    cv2.destroyAllWindows()
    cap.release()


if __name__ == "__main__":
    main()
