import os
import queue
from threading import Thread

import cv2
import numpy as np
from video_cropper.fps import FPS


class FrameReader:
    def __init__(
        self, path_to_video: str, q_size: int = 1, q_out: queue.Queue = None
    ) -> None:
        if not os.path.exists(path_to_video):
            raise ValueError("Incorrect path provided. The file doesn't exist")
        try:
            self.cap = cv2.VideoCapture(path_to_video)
            assert self.cap.isOpened()
        except Exception as e:
            print(f"Failed to init cv2.VideoCapture. Error: {e}")
            raise e
        if q_out:
            self.q = q_out
        else:
            if q_size <= 0:
                raise ValueError("Queue size cannot be negative!")
            self.q = queue.Queue(maxsize=q_size)
        self.to_stop = False
        print("Frame reader initialized")

    def start(self):
        self.t = Thread(
            target=self._decode_frame_put_in_q, args=(), daemon=True
        ).start()
        return self

    def _decode_frame_put_in_q(self) -> None:
        while True:
            if self.to_stop:
                break
            if not self.q.full():
                has_frame, frame = self.cap.read()
                if not has_frame:
                    self.stop()
                    break
                self.q.put(frame)
        print("FrameReader worker stopped")

    def stop(self) -> None:
        self.to_stop = True

    def get_frame(self) -> np.ndarray:
        return self.q.get()

    def more_frames(self) -> bool:
        return self.q.qsize() > 0


if __name__ == "__main__":
    test_video = r"D:\SingleView\SpotIQ\tests\1.flv"
    q_size = 100

    cap = cv2.VideoCapture(test_video)
    assert cap.isOpened()
    fps = FPS().start()
    while True:
        has_frame, frame = cap.read()
        if not has_frame:
            break
        frame = cv2.resize(frame, (500, 500))
        cv2.imshow("", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        fps.update()
    fps.stop()
    print("Approx FPS:", fps.get_fps())

    # frame_reader = FrameReader(test_video, q_size).start()
    # time.sleep(2)
    # fps = FPS().start()
    # while True:
    #     frame = frame_reader.get_frame()
    #     frame = cv2.resize(frame, (500, 500))
    #     cv2.imshow("", frame)
    #     if cv2.waitKey(1) & 0xFF == ord("q"):
    #         frame_reader.stop()
    #         break
    #     fps.update()
    # fps.stop()
    # print("Approx FPS:", fps.get_fps())
