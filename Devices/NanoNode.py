"""
    Copyright (C) 2020-2020
    Mikołaj Wierzbicki under thesis supervision of Paweł Kułakowski on behalf on AGH Academy of Science and Technology.
    All rights reserved

    History of Modification:
    Mikołaj Wierzbicki        Jul 31,  2020        Initial version
"""
from Vector import Vector
from Devices.Device import Device
from Devices.Router import Router
from utility import indent


class NanoNode(Device):
    """
    @classDescription:
    @author: Mikołaj Wierzbicki
    """

    def __init__(self, device_id: int, position: Vector, velocity: float, is_transmitting: bool,
                 started_within_transmission_range: bool, within_transmission_range: bool, transmission_duration: float,
                 transmission_timer: float, idle_duration: int, idle_timer: int, transmission_result, vein, router, logger) -> None:
        super().__init__('node', device_id, position)
        self.velocity = velocity
        self.is_transmitting = is_transmitting
        self.started_within_transmission_range = started_within_transmission_range
        self.within_transmission_range = within_transmission_range
        self.transmission_duration = transmission_duration
        self.transmission_timer = transmission_timer
        self.idle_duration = idle_duration
        self.idle_timer = idle_timer
        self.transmission_result = transmission_result
        self.intersections = self.position.get_sphere_intersections(router.position, router.transmission_radius)
        self.next_transmissions = self.get_next_transmissions(vein)
        self.logger = logger

    # def next_transmission(self, router):
    #     if not self.is_transmitting:
    #         while x := self.position.x <=
    #         position = self._move(self.idle_timer)
    #         if self.position.distance_from_point(router.position) <= router.transmission_radius:
    #             self.within_transmission_range = True

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
        self.is_transmitting = not self.is_transmitting

    def move_only(self, moving_time: float):
        return Vector(self.position.x + (moving_time*self.velocity), self.position.y, self.position.z)

    def move(self, moving_time: float, router: Router):
        self.position = Vector(self.position.x + (moving_time*self.velocity), self.position.y, self.position.z)
        if self.position.distance_from_point(router.position) <= router.transmission_radius:
            self.within_transmission_range = True
            # self.logger.info(f'Machine {self.device_id} is located within transmission range!')
        if self.is_transmitting:
            if self.transmission_timer > 0:
                self.transmission_timer -= 1
            else:
                if self.started_within_transmission_range and self.within_transmission_range:
                    # if self.transmission_result is None:
                    self.transmission_result = True
                    self.logger.info(indent(f'Machine {self.device_id} successfully sent data!', 8))
                self.is_transmitting = False
                self.started_within_transmission_range = False
                self.idle_timer = self.idle_duration
        else:
            if self.idle_timer > 0:
                self.idle_timer -= 1
            else:
                self.is_transmitting = True
                self.started_within_transmission_range = True if self.within_transmission_range else False
                # self.logger.info(f'Machine {self.device_id} started to transmit data within transmission range!') if self.started_within_transmission_range
                self.transmission_timer = self.transmission_duration

    def get_next_transmissions(self, vein):
        """

                :param machine:
                :return: [{positions: {
                                        start: Vector(x,y,z),
                                        end: Vector(x,y,z)
                                       },
                           time: {
                                    start: <time>,
                                    end: <end>
                                 },
                           },
                           ...,
                           ...
                          ]
                """
        within_transmission_start_time = (self.intersections[0].x - self.position.x) / self.velocity
        within_transmission_end_time = (self.intersections[1].x - self.position.x) / self.velocity
        next_transmissions = []
        if not self.is_transmitting:
            start_time = self.idle_timer
            end_time = self.idle_timer + self.transmission_duration
            start_pos = self.position.move_vector(start_time, self.velocity)
            end_pos = self.position.move_vector(end_time, self.velocity)
        else:
            start_time = 0
            end_time = self.transmission_timer
            start_pos = self.position
            end_pos = self.position.move_vector(end_time, self.velocity)

        while True:
            if self.intersections[1].x - self.intersections[0].x >= start_pos.x - end_pos.x:
                if within_transmission_end_time >=start_time >= within_transmission_start_time:
                    next_transmissions.append({'positions': {'start': start_pos, 'end': end_pos}, 'time': {'start': start_time, 'end': end_time, 'e_start': start_time, 'e_end': min(within_transmission_end_time, end_time)}})
                elif within_transmission_end_time >= end_time >= within_transmission_start_time:
                    next_transmissions.append({'positions': {'start': start_pos, 'end': end_pos}, 'time': {'start': start_time, 'end': end_time, 'e_start': max(start_time, within_transmission_start_time), 'e_end': end_time}})
            else:
                if within_transmission_end_time >= start_time >= within_transmission_start_time:
                    next_transmissions.append({'positions': {'start': start_pos, 'end': end_pos}, 'time': {'start': start_time, 'end': end_time, 'e_start': start_time, 'e_end': within_transmission_end_time}})
                elif within_transmission_end_time >= end_time >= within_transmission_start_time:
                    next_transmissions.append({'positions': {'start': start_pos, 'end': end_pos}, 'time': {'start': start_time, 'end': end_time, 'e_start': within_transmission_start_time, 'e_end': end_time}})
            start_time = end_time + self.idle_duration
            end_time = start_time + self.transmission_duration
            start_pos = self.position.move_vector(start_time, self.velocity)
            end_pos = self.position.move_vector(end_time, self.velocity)
            if end_time > 6e7 or start_pos.x >= vein.length:
                break


        # current_pos = end_pos
        # while current_pos.x < vein.length:
        #     start_time = next_transmissions[-1]['time']['end'] + self.idle_duration
        #     end_time = start_time + self.transmission_duration
        #     if end_time > 6e7:
        #         break
        #     start_pos = self.position.move_vector(start_time, self.velocity)
        #     end_pos = self.position.move_vector(end_time, self.velocity)
        #     if start_time >= within_transmission_start_time or end_time <= within_transmission_end_time:
        #         next_transmissions.append({'positions': {'start': start_pos, 'end': end_pos}, 'time': {'start': start_time, 'end': end_time}})
        #     current_pos = end_pos

        return next_transmissions

    def __repr__(self) -> str:
        return f'{self.device_type} with id {self.device_id}, position {self.position}, velocity {self.velocity}'\
                # 'transmission_status {self.transmission_status}, transmission_duration {self.transmission_duration}'\
                # 'transmission_timer {self.transmission_timer}, idle_duration {self.idle_duration}, idle_timer {self.idle_timer}'

    def __str__(self) -> str:
        return f'{self.device_type} with id {self.device_id}, position {self.position}, velocity {self.velocity}'\
                # 'transmission_status {self.transmission_status}, transmission_duration {self.transmission_duration}'\
                # 'transmission_timer {self.transmission_timer}, idle_duration {self.idle_duration}, idle_timer {self.idle_timer}'


# first_device = Device('node', 123, (1.3, 4.2, 5.2))
# print(first_device)
