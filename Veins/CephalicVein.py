"""
    Copyright (C) 2020-2020
    Mikołaj Wierzbicki under thesis supervision of Paweł Kułakowski on behalf on AGH Academy of Science and Technology.
    All rights reserved

    History of Modification:
    Mikołaj Wierzbicki        Jul 31,  2020        Initial version
"""
from typing import Tuple


class CephalicVein:
    """
    @classDescription:
    @author: Mikołaj Wierzbicki
    """

    def __init__(self, device_type: str, device_id: int, position: Tuple[float, float, float]) -> None:
        self.device_type = device_type
        self.device_id = device_id
        self.position = position
        # self.position = position

    @property
    def device_type(self) -> str:
        return self.__device_type

    @property
    def device_id(self) -> str:
        return self.__device_id

    @property
    def position(self) -> Tuple[float, float, float]:
        return self.__position

    @device_type.setter
    def device_type(self, device_type: str) -> None:
        if device_type in ['node', 'router', 'sensor']:
            self.__device_type = device_type
        else:
            raise ValueError("Unknown type of device. Only 'node', 'router' and 'sensor' types are permitted")

    @device_id.setter
    def device_id(self, device_id: int) -> None:
        if isinstance(device_id, int) and device_id >= 0:
            self.__device_id = f'{self.__device_type[0].upper()}{device_id}'
        else:
            raise ValueError("device_id must be positive integers")

    @position.setter
    def position(self, position: Tuple[float, float, float]) -> None:
        self.__position = position

    def __repr__(self) -> str:
        return f'{self.device_type} with id = {self.device_id} and position = {self.position}'

    def __str__(self) -> str:
        return f'{self.device_type} with id = {self.device_id} and position = {self.position}'
