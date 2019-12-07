import random
import os


def get_random_xy(max_x, max_y):
    return random.randint(1, max_x - 2), random.randint(1, max_y - 2)


def get_frames_from_files(frames_dir):
    frames = []
    for frame_file in os.listdir(f"{frames_dir}"):
        with open(f"{frames_dir}/{frame_file}") as _file:
            frames.append(_file.read())
    return frames
