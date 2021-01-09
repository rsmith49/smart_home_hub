from .devices.roku import RokuDevice

device_class_map = {
    RokuDevice.dev_name(): RokuDevice
}
