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


def titleize(s: str) -> str:
    """
    Titleizes a string, aka transforms it from underscored to English title
    format
    """
    s = s.replace('_', ' ')
    words = s.split(' ')
    new_words = [
        w[0].upper() + w[1:]
        for w in words
    ]

    return ' '.join(new_words)


class DescClass:
    """
    Base class for classes that require names and descriptions
    """
    _name = None
    _desc = ''

    def __init__(self, *args, **kwargs):
        if self._name is None:
            raise ValueError('_name must be specified')

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._desc
