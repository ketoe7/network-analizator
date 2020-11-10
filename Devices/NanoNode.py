"""
    Copyright (C) 2020-2020
    Mikołaj Wierzbicki under thesis supervision of Paweł Kułakowski on behalf on AGH Academy of Science and Technology.
    All rights reserved

    History of Modification:
    Mikołaj Wierzbicki        Jul 31,  2020        Initial version
"""
from Vector import Vector
from Devices.Device import Device
from typing import Tuple


class NanoNode(Device):
    """
    @classDescription:
    @author: Mikołaj Wierzbicki
    """

    def __init__(self, device_id: int, position: Vector, velocity: float, transmission_status: Tuple[bool, bool] = (True, False), within_transmission_range: bool = False, transmission_duration: float = 6.4*10**(-5), transmission_timer: float = 6.4*10**(-5), idle_duration: int = 1, idle_timer: int = 1, transmission_result=None) -> None:
        super().__init__('node', device_id, position)
        self.velocity = velocity
        self.transmission_status = {'transmit': transmission_status[0], 'started_within_transmission_range': transmission_status[1]}
        self.within_transmission_range = within_transmission_range
        self.transmission_duration = transmission_duration
        self.transmission_timer = transmission_timer
        self.idle_duration = idle_duration
        self.idle_timer = idle_timer
        self.transmission_result = transmission_result

    @property
    def velocity(self) -> float:
        return self.__velocity

    @property
    def transmission_duration(self) -> int:
        return self.__transmission_duration

    @property
    def transmission_timer(self) -> int:
        return self.__transmission_timer

    @property
    def idle_duration(self) -> int:
        return self.__idle_duration

    @property
    def idle_timer(self) -> int:
        return self.__idle_timer

    @velocity.setter
    def velocity(self, velocity: int) -> None:
        if velocity > 0:
            self.__velocity = velocity
        else:
            raise ValueError("Machine's velocity must be positive number")

    @transmission_duration.setter
    def transmission_duration(self, transmission_duration: int) -> None:
        if transmission_duration > 0:
            self.__transmission_duration = transmission_duration
        else:
            raise ValueError("transmission_duration must be positive number")

    @transmission_timer.setter
    def transmission_timer(self, transmission_timer: int) -> None:
        if 0 <= transmission_timer <= self.transmission_duration:
            self.__transmission_timer = transmission_timer
        else:
            raise ValueError(f"transmission_timer must be positive number between 0 and {self.transmission_duration}")

    @idle_duration.setter
    def idle_duration(self, idle_duration: int) -> None:
        if isinstance(idle_duration, int) and idle_duration >= 0:
            self.__idle_duration = idle_duration
        else:
            raise ValueError("idle_duration must be positive integers")

    @idle_timer.setter
    def idle_timer(self, idle_timer: int) -> None:
        if 0 <= idle_timer <= self.idle_duration:
            self.__idle_timer = idle_timer
        else:
            raise ValueError(f"transmission_timer must be positive number between 0 and {self.idle_duration}")

    def change_transmission_status(self):
        self.transmission_status = not self.transmission_status

    def move(self, moving_time: float):
        self.position = Vector(self.position.x + (moving_time*self.velocity), self.position.y, self.position.z)

    def __repr__(self) -> str:
        return f'{self.device_type} with id {self.device_id}, position {self.position}, velocity {self.velocity}'\
                # 'transmission_status {self.transmission_status}, transmission_duration {self.transmission_duration}'\
                # 'transmission_timer {self.transmission_timer}, idle_duration {self.idle_duration}, idle_timer {self.idle_timer}'

    def __str__(self) -> str:
        return f'{self.device_type} with id {self.device_id}, position {self.position}, velocity {self.velocity}'\
                # 'transmission_status {self.transmission_status}, transmission_duration {self.transmission_duration}'\
                # 'transmission_timer {self.transmission_timer}, idle_duration {self.idle_duration}, idle_timer {self.idle_timer}'

class Pair():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __format__(self, spec):
        return "{}{}{}".format(self.x, spec, self.y)

    def __str__(self):
        return "{:/}".format(self, 'miki')

    def __repr__(self):
        return "Pair({}, {})".format(self.x, self.y)


# pair = Pair(1, 2)
# print(pair)


# first_device = Device('node', 123, (1.3, 4.2, 5.2))
# print(first_device)
