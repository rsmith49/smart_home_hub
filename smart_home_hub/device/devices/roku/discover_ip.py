import upnpclient

from marshmallow import fields

from smart_home_hub.device.base_device import DeviceAction


def list_available_devices() -> list:
    """
    Method to return list of available device names on the network
    """
    devices = upnpclient.discover()

    return [d.friendly_name for d in devices]


def discover_ip(device_name) -> str:
    """
    Method to return the URL (IP) to send requests to for a roku device of
    the given name
    :param device_name: Name of device we are searching for
    :return: An IP address string that can be used to send requests
    :raises: ValueError if no such device is found
    """
    devices = upnpclient.discover()

    roku_device = [
        d for d in devices
        if device_name.lower() == d.friendly_name.lower()
    ]

    if len(roku_device) == 0:
        raise ValueError(f'No device found for name {device_name}')

    return roku_device[0].location


class SetIP(DeviceAction):
    _name = 'set_device_ip'
    _desc = """
        Sets the Roku device IP based on the available devices on this network.
        If no device matching the name can be discovered, or if device_name is
        null, will return a list of available devices on the network.
    """

    def argmap(self) -> dict:
        return {
            'device_name': fields.Str(required=True)
        }

    def perform(self):
        name = self.args['device_name']

        if name is not None:
            try:
                self.device.config['ip'] = discover_ip(name)
                self.device.config.save()
                return
            except ValueError:
                # Continuing to return list of available devices
                self.resp['message'] = f'Could not find device {name}. '

        available_devices = list_available_devices()
        self.resp['available_devices'] = available_devices
        self.resp['message'] += f'Available Device Names: {", ".join(available_devices)}'
