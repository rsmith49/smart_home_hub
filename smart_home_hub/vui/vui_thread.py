"""
UPDATE: This will be like an API, and we will call both threads from one main
        program loop. Be sure to use Locks and Events and everything.

This file contains the main class used as the controller for the program loop.

This code will be primarily modified from other sources, as I still get a
handle on how to properly set this kind of project up.
"""
from marshmallow import fields

from smart_home_hub.devices import device_class_map
from smart_home_hub.devices.base_device import Device, DeviceAction
from .general_actions import GenericDevice
from .stt import SpeechToText, CommandParser


class NextCommandException(Exception):

    def __init__(self, msg):
        super().__init__()
        self.msg = msg


def get_context():
    # TODO: Make this work
    pass


class VUI:
    # TODO: Make the device_name_from and action_name_from work for multi-word
    #       named devices and actions (and args I guess)

    def __init__(self, tts, stt: SpeechToText):
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
        general_actions = GenericDevice().action_map().keys()

        if context is not None and context.get('device'):
            device_name = context['device']
        else:
            device_name = input_.words[0]

            # Cutting off logic if the first element of the input string is
            # a general action
            if device_name in general_actions:
                # We do not pop here bc the device_name is actually an action,
                # and should be interpreted on the next step
                return GenericDevice(context=context)
            else:
                input_.pop()

        try:
            return device_class_map[device_name](
                context=context
            )
        except KeyError:
            raise NextCommandException(f"No device named {device_name}")

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
                action_name = input_.pop()
            except IndexError:
                raise NextCommandException(f"Must specify an action")

        try:
            return device.action_map()[action_name]
        except KeyError:
            raise NextCommandException(
                f"No action named {action_name} for device {device.name}"
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
                self.tts(f'Give a value for {arg_name}')
                args[arg_name] = CommandParser(
                    self.stt.listen()
                ).pop_as_type(arg)

        for arg_name, arg in default_args:
            if arg_name not in args:
                args[arg_name] = arg.missing

        action.init_args(**args)

    def run(self):
        """
        Runs the main VUI driver
        """
        while True:
            try:
                if self.prompt is not None:
                    self.tts(self.prompt)

                context = get_context()

                if context is None or not context.get('in_dialogue'):
                    # TODO: Do this wakeword better. Maybe have it be constructor arg to STT
                    self.stt.listen_for_wakeword('Jarvis')
                    self.tts('Listening...')

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
