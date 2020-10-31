import os


def create_dirs_for(filepath):
    """
    Method to create any necessary directories for a file before writing
    to that file
    :param filepath: String to location of the filepath
    """
    # Otherwise, don't have to create any directories
    if filepath.find('/') > -1:
        dir_path = filepath[:filepath.rfind('/')]
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
