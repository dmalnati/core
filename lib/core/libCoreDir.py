import os


def CorePath(path):
    core = os.environ["CORE"]

    return core + path


