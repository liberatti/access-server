import os
import sys
import threading


def handle_sigterm(signum, frame):
    threads_ativos = threading.enumerate()
    for thread in threads_ativos:
        thread.active = False
    sys.exit(0)


def chmod_r(path, mode, recursive=False):
    if recursive:
        for root, dirs, files in os.walk(path):
            for dirname in dirs:
                os.chmod(os.path.join(root, dirname), mode)
            for filename in files:
                os.chmod(os.path.join(root, filename), mode)
    os.chmod(path, mode)
