import upnpclient


def keypress_endpoint(event):
    """
    Helper method to return the endpoint for the corresponding keypress event
    :param event: Name of the event (ex: powerOn/powerOff)
    :return: A string of the URL to hit
    """
    return f'/keypress/{event}'


def discover_ip(device_name):
    """
    Method to return the URL (IP) to send requests to for a roku device of
    the given name
    :param device_name: Name of device we are seareching for
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
