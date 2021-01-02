"""
This file contains a class to parse a text command once it has been translated
from speech to text
"""
from typing import List
from word2number import w2n

from smart_home_hub.utils.argmap_utils import FIELD_TO_STR_MAP


class CommandParser:

    def __init__(self, command):
        self.original_command = command
        self.words = command.lower().split(' ')

    def prefix_from(self, phrases: List[str], pop_if_true=True):
        """
        Checks through each of the phrases passed to see if they are present at
        the start of the command. Returns the first prefix present, or None.

        NOTE: Converts _ to space in each phrase checked. This is mainly done
              for device and action names to be compatible.

        :param phrases: A list of strings representing the phrases
        :param pop_if_true: Whether to pop the phrase from head if found
        :return: Either the phrase that was found, or None if no phrase matched
        """
        for phrase in phrases:
            if self.head_is(phrase.replace('_', ' '), pop_if_true=pop_if_true):
                return phrase

        return None

    def head_is(self, phrase, pop_if_true=True):
        """
        Checks if the head of the command is the phrase given
        :param phrase: Can be a single word (str), list of words, or phrase
        :param pop_if_true: Whether to pop the relevant words from the command
                            if the phrase is included
        :return: True if the phrase is the head of the command
        """
        if type(phrase) is str:
            phrase = phrase.split(' ')
        phrase = [word.lower() for word in phrase]

        if self.words[:len(phrase)] == phrase:
            if pop_if_true:
                self.pop(len(phrase))
            return True

        else:
            return False

    def pop(self, num_words=1):
        """
        Returns the first num_words words as a string, and removes them from
        the command
        """
        to_ret = self.words[:num_words]
        self.words = self.words[num_words:]

        return ' '.join(to_ret)

    def pop_as_type(self, field, *args, **kwargs):
        """
        Pops the desired words/phrase, but returns the value as the type
        specified by the marshmallow field (or string) passed
        :param field: Either a string, or a marshmallow field
        :return: popped phrase in the type specified
        """
        if type(field) is not str:
            field = FIELD_TO_STR_MAP[type(field)]

        phrase = self.pop(*args, **kwargs)

        if field == 'string':
            return phrase
        elif field == 'integer':
            try:
                return int(phrase)
            except ValueError:
                return w2n.word_to_num(phrase)
        elif field == 'float':
            try:
                return float(phrase)
            except ValueError:
                return w2n.word_to_num(phrase)
        elif field == 'boolean':
            return bool(phrase)
        else:
            raise ValueError(f'Cannot parse arg of type {field}')
