import os


def get_frames_from_files(frames_dir):
    frames = []
    for frame_file in os.listdir(f"/{frames_dir}"):
        with open(f"{frames_dir}/{frame_file}") as _file:
            frames.append(_file.read())
    return frames


print(os.listdir(f"rocket_frames"))
