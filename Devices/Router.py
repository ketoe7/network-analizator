"""
    Copyright (C) 2020-2020
    Mikołaj Wierzbicki under thesis supervision of Paweł Kułakowski on behalf on AGH Academy of Science and Technology.
    All rights reserved

    History of Modification:
    Mikołaj Wierzbicki        Jul 31,  2020        Initial version
"""
from Vector import Vector
from Devices.Device import Device


class Router(Device):
    """
    @classDescription:
    @author: Mikołaj Wierzbicki
    """

    def __init__(self, device_id: int, position: Vector, transmission_radius: float = 0.1) -> None:
        super().__init__('router', device_id, position)
        self.transmission_radius = transmission_radius

    @property
    def transmission_radius(self) -> float:
        return self.__transmission_radius

    @transmission_radius.setter
    def transmission_radius(self, transmission_radius: float) -> None:
        try:
            self.__transmission_radius = float(transmission_radius)
        except ValueError:
            raise ValueError(f'Cannot assign {transmission_radius} to float variable')

    def __repr__(self) -> str:
        return f'{self.device_type} with id = {self.device_id} and position = {self.position}'


# first_device = Device('node', 123, (1.4, 2.3, 5.9))
# print(first_device)
