import os

import cv2


def main():
    SAVE_PATH = r""
    ad_times = [
        (5 * 60 + 54, 6 * 60 + 7),
        (7 * 60 + 8, 7 * 60 + 22),
        (7 * 60 + 23, 7 * 60 + 37),
        (7 * 60 + 53, 8 * 60 + 7),
        (14 * 60 + 49, 14 * 60 + 59),
        (15 * 60 + 1, 15 * 60 + 15),
        (15 * 60 + 16, 15 * 60 + 30),
        (16 * 60 + 30, 16 * 60 + 45),
        (16 * 60 + 46, 17 * 60 + 0),
        (17 * 60 + 1, 17 * 60 + 15),
        (23 * 60 + 51, 24 * 60 + 6),
        (24 * 60 + 21, 24 * 60 + 36),
        (24 * 60 + 37, 24 * 60 + 51),
        (25 * 60 + 6, 25 * 60 + 21),
        (25 * 60 + 52, 26 * 60 + 21),
        #(0 * 60 +, 0 * 60 +),

    ]
    path_to_video = r"D:\SingleView\SpotIQ\tests\6.flv"
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
