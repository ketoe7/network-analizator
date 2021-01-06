"""
    Copyright (C) 2020-2020
    Mikołaj Wierzbicki under thesis supervision of Paweł Kułakowski on behalf on AGH Academy of Science and Technology.
    All rights reserved

    History of Modification:
    Mikołaj Wierzbicki        Jul 31,  2020        Initial version
"""
from Vector import Vector

class Vein:
    """
    @classDescription:
    @author: Mikołaj Wierzbicki
    """

    def __init__(self, name: str, length: float, radius: float, velocity: float) -> None:
        self.name = name
        self.velocity = velocity
        self.radius = radius
        self.length = length
        self.abstract_length = Vector.speed_for_d(self.velocity, self.radius, self.radius - transmission_radius_range) * simulation_time

    @property
    def name(self) -> str:
        return self.__name

    @property
    def length(self) -> float:
        return self.__length

    @property
    def radius(self) -> float:
        return self.__radius

    @property
    def velocity(self) -> float:
        return self.__velocity

    @name.setter
    def name(self, name: str) -> None:
        if isinstance(name, str):
            self.__name = name
        else:
            raise ValueError("Vein's name must be string")

    @length.setter
    def length(self, length: float) -> None:
        if float(length) > 0:
            self.__length = float(length)
        else:
            raise ValueError("Vein's length must be positive number")

    @radius.setter
    def radius(self, radius: float) -> None:
        if float(radius) > 0:
            self.__radius = float(radius)
        else:
            raise ValueError("Vein's radius must be positive number")

    @velocity.setter
    def velocity(self, velocity: float) -> None:
        if float(velocity) > 0:
            self.__velocity = float(velocity)
        else:
            raise ValueError("Vein's velocity must be positive number")

    def __repr__(self) -> str:
        return f'{self.name} with length = {self.length} and radius = {self.radius}'
