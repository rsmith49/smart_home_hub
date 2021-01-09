import os, sys

from dotenv import load_dotenv, find_dotenv
from subprocess import call

sys.path.append(os.getcwd())


def main():
    load_dotenv(find_dotenv(raise_error_if_not_found=True, usecwd=True))
    call([
        'cp',
        '-R',
        'initial_config',
        os.environ['SHH_CONFIG_BASE_DIR']
    ])


if __name__ == '__main__':
    main()
