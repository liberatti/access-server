import os
import sys
import threading
import config


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


def get_template_path(filename):
    """Resolve template file path using config.BASE_BATH or config.main_path.

    :param filename: Template file name.
    :type filename: str
    :return: Absolute or resolved path to template file.
    :rtype: str
    """
    path = os.path.join(getattr(config, "BASE_BATH", "/opt/access-server"), "templates", filename)
    if not os.path.exists(path):
        path = os.path.join(config.main_path, "templates", filename)
    return path
