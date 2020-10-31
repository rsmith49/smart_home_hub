import json
import os

from abc import ABCMeta, abstractmethod
from collections import MutableMapping
from copy import deepcopy
from typing import Union

from .env_consts import CONFIG_BASE_DIR
from .utils import create_dirs_for


class ConfigMap:
    """
    This class represents a mapping for configuration files. It provides a way
    to manipulate the mapping more easily with multiple methods.
    """

    def __init__(self, mapping_dict, required_keys=None, internal_keys=None):
        """
        :param mapping_dict: Dict mapping of key, value pairs in the structure
                             of the config, where any value specified is the
                             default value of an empty config
        :param required_keys: A list of required keys to specify
                              NOTE: Top level only
        :param internal_keys: A list of keys that can only be modified
                              internally (aka not through a request)
                              NOTE: Top level only
        """
        self.default_mapping = deepcopy(mapping_dict)
        self.required_keys = required_keys
        self.internal_keys = internal_keys


class Config(MutableMapping, metaclass=ABCMeta):
    """
    This is an abstract class representing a configuration object, that can be
    saved, loaded, modified, and deleted from the corresponding file.
    """
    def __init__(self):
        self.content = None

        try:
            self.load()
            self.file_exists = True
        except FileNotFoundError:
            # TODO: Figure out best way to specify defaults
            self.init_default_content()
            self.file_exists = False

    def save(self):
        """
        Saves the config file in self.filepath (overwriting current file)
        """
        create_dirs_for(self.filepath)

        with open(self.filepath, 'w') as config_file:
            json.dump(self.content, config_file, indent=2)

        self.file_exists = True

    def load(self):
        """
        Loads the config from self.filepath into self.content
        """
        with open(self.filepath) as config_file:
            self.content = json.load(config_file)

    def delete(self):
        """
        Deletes the config file in self.filepath (but not self.content)
        """
        os.remove(self.filepath)

        self.file_exists = False

    def dig(self, *keys):
        """
        A method to emulate Ruby's Hash.dig method, accessing a nested
        attribute in self.content more easily
        :param keys: varargs list of keys representing the nested path
        :return: Value of the accessed attribute
        """
        val = self.content
        for key in keys:
            val = val[key]

        return val

    def has_changes(self):
        """
        Helper method to check if self.content differs from the config stored
        in self.filepath
        """
        old_content = self.content
        try:
            self.load()
        except FileNotFoundError:
            return True

        has_changes = old_content != self.content
        self.content = old_content

        return has_changes

    def init_default_content(self):
        """
        Method to initialize the self.content dict with the defaults specified
        in self.config_map()
        """
        config_map = self.config_map()
        if type(config_map) is dict:
            config_map = ConfigMap(config_map)

        self.content = deepcopy(config_map.default_mapping)

    @property
    def filepath(self):
        return CONFIG_BASE_DIR + self.rel_filepath()

    @abstractmethod
    def rel_filepath(self) -> str:
        """
        Method to implement. Should return the relative filepath to where this
        config file would be stored - can use attributes of self if needed
        """

    @classmethod
    @abstractmethod
    def config_map(cls) -> Union[ConfigMap, dict]:
        """
        Method to implement. Should return a ConfigMap object
        """

    # Defining dict access methods

    def __setitem__(self, k, v):
        self.content[k] = v

    def __delitem__(self, v):
        self.content.__delitem__(v)

    def __getitem__(self, k):
        return self.content[k]

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        return self.content.__iter__()
