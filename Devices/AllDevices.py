"""
    Copyright (C) 2020-2020
    Mikołaj Wierzbicki under thesis supervision of Paweł Kułakowski on behalf on AGH Academy of Science and Technology.
    All rights reserved

    History of Modification:
    Mikołaj Wierzbicki        Jul 31,  2020        Initial version
"""
from Devices.Device import Device
from Devices.NanoNode import NanoNode
from Devices.Router import Router
from typing import List


class AllDevice:
    """
    @classDescription:
    @author: Mikołaj Wierzbicki
    """

    def __init__(self, devices: List[Device] = None) -> None:
        self.devices = [] if devices is None else devices
        self.nano_nodes = []
        self.router = None
        for device in self.devices:
            if isinstance(device, NanoNode):
                self.nano_nodes.append(device)
            elif isinstance(device, Router):
                self.router = device

    @property
    def devices(self) -> List[Device]:
        return self.__devices

    @devices.setter
    def devices(self, devices: List[Device]) -> None:
        # TODO: validate
        self.__devices = devices

    def add_device(self, device: Device) -> None:
        if isinstance(device, Device):
            self.devices.append(device)
            if isinstance(device, NanoNode):
                self.nano_nodes.append(device)
            elif isinstance(device, Router):
                self.router = device
        else:
            raise ValueError('Cannot add to devices none "Device" object')

    def __repr__(self) -> str:
        all_devices_repr = '\n'.join([dev.__repr__() for dev in self.devices])
        return f'List of all devices:\n{all_devices_repr}'

# all_devices = AllDevice([Device('node', 123, (1.3, 1.5, 5.2)), Device('router', 124, (2.3, 2.5, 6.2))])
# print(all_devices)
