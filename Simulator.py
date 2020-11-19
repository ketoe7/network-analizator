from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from Devices.NanoNode import NanoNode
from Devices.Router import Router
from Veins.Vein import Vein
from Vector import Vector
from utility import indent
from time import sleep
import random
# import numpy as np


def move_wrapper(machine, vein, time_sample, router, testing_machines):
    if machine.position.x <= vein.length / 2 and not machine.transmission_result:
        machine.move(time_sample, router)
    else:
        testing_machines.remove(machine)
    return machine.device_id


class Simulator:
    def __init__(self, iteration_number, logger, nano_machines_amount, vein: Vein, transmission_radius_range=0.1, time_sample=1,
                 simulation_time=10**6, transmission_duration=64, idle_duration=10**6, router_position='top', collision=False, verbose=False):
        self.iteration_number = iteration_number
        self.simulation_time = simulation_time
        self.transmission_radius_range = transmission_radius_range
        self.time_sample = time_sample
        self.transmission_duration = transmission_duration
        self.idle_duration = idle_duration
        self.potential_machines = []
        self.vein = vein
        self.router = None
        self.nano_machines = self.testing_machines =[]
        self.verbose = verbose
        self.logger = logger
        self.collisions = self.failed_transmissions = self.successful_transmissions = 0
        self.generate_data(nano_machines_amount, router_position, collision)

    def generate_data(self, nodes_within_cephalic_vein, router_position, collision):
        vein_diameter_start = Vector(-1 * (self.vein.length / 2), 0, 0)
        vein_diameter_end = Vector(self.vein.length / 2, 0, 0)
        if router_position == 'top':
            self.router = Router(1, Vector((self.vein.length/2) - self.transmission_radius_range, 0, self.vein.radius), self.transmission_radius_range)
        elif router_position == 'center':
            self.router = Router(1, Vector((self.vein.length/2) - self.transmission_radius_range, 0, 0), self.transmission_radius_range)
        dev_id = 1
        counter = 0
        while counter < nodes_within_cephalic_vein:
            x = random.uniform(-1 * (self.vein.length / 2), self.router.position.x - self.router.transmission_radius)
            y = random.uniform(-1 * self.vein.radius, self.vein.radius)
            z = random.uniform(-1 * self.vein.radius, self.vein.radius)
            machine_position = Vector(x, y, z)
            distance_from_diameter = machine_position.distance_from_line(vein_diameter_start, vein_diameter_end)
            if distance_from_diameter < self.vein.radius:
                counter += 1
                machine_velocity = self.vein.velocity * 2 * (self.vein.radius ** 2 - distance_from_diameter ** 2) / (self.vein.radius ** 2)
                transmit = random.choices([False, True], weights=(93.6, 6.4), k=1)[0]
                if transmit:
                    transmission_timer = random.choice(range(0, self.transmission_duration))
                    idle_timer = self.idle_duration
                else:
                    idle_timer = random.choice(range(0, self.idle_duration))
                    transmission_timer = self.transmission_duration

                if machine_position.can_cross_transmission_range(self.router):
                    self.nano_machines.append(NanoNode(dev_id,
                                                       machine_position,
                                                       machine_velocity,
                                                       is_transmitting=transmit,
                                                       started_within_transmission_range=False,
                                                       within_transmission_range=False,
                                                       transmission_duration=self.transmission_duration,
                                                       transmission_timer=transmission_timer,
                                                       idle_duration=self.idle_duration,
                                                       idle_timer=idle_timer,
                                                       transmission_result=False,
                                                       logger=self.logger
                                                       )
                                              )
                    dev_id += 1
        self.testing_machines = list(self.nano_machines)
        ##### Generate Collision #####
        if collision:
            self.logger.info(indent(f'First 2 machines: {self.testing_machines[0].device_id} and {self.testing_machines[1].device_id}', 6))
            self.testing_machines[0].position = Vector(self.router.position.x - self.transmission_radius_range + 0.01, self.router.position.y - self.transmission_radius_range + 0.01, self.router.position.z - self.transmission_radius_range + 0.01)
            self.testing_machines[0].within_transmission_range = True
            self.testing_machines[0].transmission_result = False
            self.testing_machines[0].idle_timer = 1
            self.testing_machines[0].transmission_timer = self.transmission_duration
            self.testing_machines[1].position = Vector(self.router.position.x - self.transmission_radius_range + 0.02, self.router.position.y - self.transmission_radius_range + 0.02, self.router.position.z - self.transmission_radius_range + 0.02)
            self.testing_machines[1].within_transmission_range = True
            self.testing_machines[1].transmission_result = False
            self.testing_machines[1].idle_timer = 2
            self.testing_machines[1].transmission_timer = self.transmission_duration

        return True

    def remove_nano_machine(self, machine):
        self.nano_machines.remove(machine)

    # def move_wrapper(self, machine):
    #     if machine.position.x <= self.vein.length / 2 and not machine.transmission_result:
    #         machine.move(self.time_sample, self.router)
    #     else:
    #         self.testing_machines.remove(machine)
    #     return machine.device_id

    def run_simulation(self):
        self.logger.info(indent(f'{len(self.nano_machines)} machines are potential to transmit data data', 6))
        while self.testing_machines:
        # print(int(self.simulation_time / self.time_sample))
        # sleep(5)
        # for _ in [self.time_sample * _ for _ in range(int(self.simulation_time / self.time_sample))]:
        #     print(f'dziwny loop: {_}')
        #     processes = []
            for machine in list(self.testing_machines):
                # p = multiprocessing.Process(target=move_wrapper, args=[machine, self.vein, self.time_sample, self.router, self.testing_machines])
                # p.start()
                # processes.append(p)
                # for process in processes:
                #     process.join()
                if machine.position.x <= self.vein.length / 2 and not machine.transmission_result:
                    machine.move(self.time_sample, self.router)
                else:
                    self.testing_machines.remove(machine)

            transmitting_machines_within_range = [machine for machine in self.testing_machines if machine.within_transmission_range and machine.is_transmitting]
            if len(transmitting_machines_within_range) > 1:
                self.logger.info(indent(f'There is collision between machines {" and ".join(str(m) for m in transmitting_machines_within_range)}', 6))
                self.testing_machines = [m for m in self.testing_machines if m not in transmitting_machines_within_range]
                self.collisions += 1

        self.failed_transmissions = len(list(filter(lambda m: not m.transmission_result, self.nano_machines)))
        self.successful_transmissions = len(list(filter(lambda m: m.transmission_result, self.nano_machines)))
        return self.successful_transmissions, self.failed_transmissions, self.collisions
