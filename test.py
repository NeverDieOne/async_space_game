import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_rocket_frames():
    frames = []
    rocket_dir = os.path.join(BASE_DIR, 'rocket_frames')
    for frame_file in os.listdir(rocket_dir):
        with open(os.path.join(rocket_dir, frame_file)) as _file:
            frames.append(_file.read())
    return frames


print(get_rocket_frames())
