import random
import string
import time
import os
import shutil


def random_string(n):
    """Generates a random string of length n.

    Parameters
    ----------
    n : int
        The length of the generated string.

    Returns
    -------
    random_str : str
        The randomly generated string.

    """
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


def remove_file(file_path):
    """Deletes the file at the given filepath if it exists.

    Parameters
    ----------
    file_path : str
        The path of the file that should be deleted.

    Returns
    -------
    None

    """
    print('Deleting file {}'.format(file_path))
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("Cannot remove the file {}. It does not exist.".format(file_path))


def remove_directory(dir_path):
    """Deletes the directory and all of the files inside it at the given filepath if it exists.

    Parameters
    ----------
    dir_path : str
        The path to the directory that should be deleted.

    Returns
    -------
    None

    """
    print('Deleting directory {}'.format(dir_path))
    try:
        shutil.rmtree(dir_path)
    except Exception as err:
        print(err)
        print('Cannot delete the directory {}.'.format(dir_path))


class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
