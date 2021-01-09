"""
UPDATE: This will be like an API, and we will call both threads from one main
        program loop. Be sure to use Locks and Events and everything.

This file contains the main class used as the controller for the program loop.

This code will be primarily modified from other sources, as I still get a
handle on how to properly set this kind of project up.
"""
from marshmallow import fields

from smart_home_hub.device import device_class_map
from smart_home_hub.device.base_device import Device, DeviceAction
from smart_home_hub.utils.config import Config
from .general_actions import GenericDevice
from .stt import SpeechToText, CommandParser
from .tts import TextToSpeech


class NextCommandException(Exception):

    def __init__(self, msg):
        super().__init__()
        self.msg = msg


# TODO: Would we rather have a shared config between VUI and API?
class VUIContext(Config):
    """
    The context Config used by the VUI thread.
    """
    def rel_filepath(self) -> str:
        return 'vui_context.json'

    @classmethod
    def config_map(cls):
        return {}


class VUI:
    """
    Main driver for the voice activated commands
    """

    def __init__(self, tts: TextToSpeech, stt: SpeechToText):
        """
        :param tts: Text to speech object
        :param stt: Speech to text object
        """
        self.tts = tts
        self.stt = stt

        self.prompt = None

    def device_from(self, input_: CommandParser, context) -> Device:
        """
        Returns the Device to use based on the input string and current context
        :param input_: CommandParser of string interpreted by the stt engine
        :param context: A dict of JSON context surrounding the command
        :return: The Device object we are retrieving
        """
        general_actions = GenericDevice().action_names()
        if input_.prefix_from(general_actions, pop_if_true=False):
            # Cutting off logic if the first element of the input string is
            # a general action
            return GenericDevice(context=context)

        if context is not None and context.get('device'):
            device_name = context['device']
        else:
            device_name = input_.prefix_from(device_class_map.keys())

        try:
            return device_class_map[device_name](
                context=context
            )
        except KeyError:
            raise NextCommandException(f"No device named {input_.pop()}")

    def action_from(self, input_: CommandParser, context, device) -> DeviceAction:
        """
        Returns the Action to run based on the input, context and device
        :param device: Device object to find the action from
        :return: A DeviceAction object
        """
        if context is not None and context.get('action'):
            action_name = context['action']
        else:
            try:
                action_name = input_.prefix_from(device.action_names())
            except IndexError:
                raise NextCommandException(f"Must specify an action")

        try:
            return device.action_map()[action_name]
        except KeyError:
            raise NextCommandException(
                f"No action named {input_.pop()} for device {device.name}"
            )

    def init_args_from(self, input_: CommandParser, context, action):
        """
        Initializes the args for the action based on the input, context, and
        argmap
        :param action: The DeviceAction to have args initialized
        """
        # TODO: Can maybe even use the tts and stt here
        args = {}

        # TODO: Maybe hit these all at once on one loop?
        ordered_args = sorted(
            [
                (arg_name, arg) for arg_name, arg in action.argmap().items()
                if 'voice_ndx' in arg.metadata
            ],
            key=lambda x: x[1].metadata['voice_ndx']
        )
        required_args = [
            (arg_name, arg) for arg_name, arg in action.argmap().items()
            if arg.required
        ]
        default_args = [
            (arg_name, arg) for arg_name, arg in action.argmap().items()
            if arg.missing != fields.missing_
        ]

        for arg_name, arg in ordered_args:
            if len(input_.words) > 0:
                # TODO: Datatype conversion based on arg
                args[arg_name] = input_.pop_as_type(arg)

        for arg_name, arg in required_args:
            if arg_name not in args:
                # TODO: Specify more stuff here probably
                # TODO: A lot more stuff here (datatype, arg info, multiple args at once).
                #       Maybe its own function
                self.tts.speak(f'Give a value for {arg_name}')

                command = CommandParser(self.stt.listen())
                args[arg_name] = command.pop_as_type(
                    arg,
                    num_words=len(command.words)
                )

        for arg_name, arg in default_args:
            if arg_name not in args:
                args[arg_name] = arg.missing

        action.init_args(**args)

    def run(self):
        """
        Runs the main VUI driver
        """
        # Clearing context at start to have a fresh run
        context = VUIContext()
        context.clear()
        context.save()

        while True:
            try:
                if self.prompt is not None:
                    self.tts.speak(self.prompt)

                context = VUIContext()

                if context is None or not context.get('in_dialogue'):
                    # TODO: Do this wakeword better. Maybe have it be constructor arg to STT
                    self.stt.listen_for_wakeword('Jarvis')
                    self.tts.recognize_wakeword()

                input_ = CommandParser(self.stt.listen())

                # TODO: Do this better too
                if input_.head_is('quit'):
                    return

                device = self.device_from(input_, context)
                action = self.action_from(input_, context, device)
                self.init_args_from(input_, context, action)

                action.perform()
                self.prompt = action.response()['message']

            except NextCommandException as e:
                self.prompt = e.msg
