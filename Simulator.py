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
import copy
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
        self.nano_machines = []
        self.testing_machines = []
        self.collisions = []
        self.verbose = verbose
        self.logger = logger
        # self.collisions = 0
        self.failed_transmissions = 0
        self.successful_transmissions = 0
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
            if collision and (counter == 0 or counter == 1):
                if counter == 0:
                    machine_position = Vector(self.router.position.x - self.transmission_radius_range + 0.001, 0, self.router.position.z - 0.001)
                else:
                    machine_position = Vector(self.router.position.x - self.transmission_radius_range + 0.002, 0, self.router.position.z - 0.002)

            else:
                x = random.uniform(-1 * (self.vein.length / 2), self.router.position.x - self.router.transmission_radius)
                y = random.uniform(-1 * self.vein.radius, self.vein.radius)
                z = random.uniform(-1 * self.vein.radius, self.vein.radius)
                machine_position = Vector(x, y, z)
            distance_from_diameter = machine_position.distance_from_line(vein_diameter_start, vein_diameter_end)
            if distance_from_diameter < self.vein.radius - 0.00001:
                counter += 1
                machine_velocity = self.vein.velocity * 2 * (self.vein.radius ** 2 - distance_from_diameter ** 2) / (self.vein.radius ** 2)
                if collision and (counter == 1 or counter == 2):
                    transmit = False
                    idle_timer = counter
                    transmission_timer = self.transmission_duration
                else:
                    transmit = random.choices([False, True], weights=(93.6, 6.4), k=1)[0]
                    if transmit:
                        transmission_timer = random.choice(range(0, self.transmission_duration))
                        idle_timer = self.idle_duration
                    else:
                        idle_timer = random.choice(range(0, self.idle_duration))
                        transmission_timer = self.transmission_duration

                # if machine_position.can_cross_transmission_range(self.router):
                if collision and (counter == 1 or counter == 2):
                    print(machine_position.get_sphere_intersections(self.router.position, self.transmission_radius_range))

                if machine_position.get_sphere_intersections(self.router.position, self.transmission_radius_range):
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
                                                       vein=self.vein,
                                                       router=self.router,
                                                       logger=self.logger
                                                       )
                                              )
                    if collision and (counter == 1 or counter == 2):
                        print(self.nano_machines[counter-1])
                    dev_id += 1
        self.testing_machines = list(self.nano_machines)
        ##### Generate Collision #####
        # if collision:
        #     self.logger.info(indent(f'First 2 machines: {self.nano_machines[0]} and {self.nano_machines[1]}', 6))
        #     self.nano_machines[0].position = Vector(self.router.position.x - self.transmission_radius_range + 0.01, self.router.position.y - self.transmission_radius_range + 0.01, self.router.position.z - self.transmission_radius_range + 0.01)
        #     self.nano_machines[0].within_transmission_range = True
        #     self.nano_machines[0].transmission_result = False
        #     self.nano_machines[0].idle_timer = 1
        #     self.nano_machines[0].transmission_timer = self.transmission_duration
        #     self.nano_machines[1].position = Vector(self.router.position.x - self.transmission_radius_range + 0.02, self.router.position.y - self.transmission_radius_range + 0.02, self.router.position.z - self.transmission_radius_range + 0.02)
        #     self.nano_machines[1].within_transmission_range = True
        #     self.nano_machines[1].transmission_result = False
        #     self.nano_machines[1].idle_timer = 2
        #     self.nano_machines[1].transmission_timer = self.transmission_duration

        return True

    def remove_nano_machine(self, machine):
        self.nano_machines.remove(machine)

    # def next_transmissions(self, machine: NanoNode):
    #     """
    #
    #     :param machine:
    #     :return: [{positions: {
    #                             start: Vector(x,y,z),
    #                             end: Vector(x,y,z)
    #                            },
    #                time: {
    #                         start: <time>,
    #                         end: <end>
    #                      },
    #                },
    #                ...,
    #                ...
    #               ]
    #     """
    #     next_transmissions = []
    #     if not machine.is_transmitting:
    #         start_time = machine.idle_timer
    #         end_time = machine.idle_timer + machine.transmission_duration
    #         start_pos = machine.position.move_vector(start_time, machine.velocity)
    #         end_pos = machine.position.move_vector(end_time, machine.velocity)
    #     else:
    #         start_time = 0
    #         end_time = machine.transmission_timer
    #         start_pos = machine.position
    #         end_pos = machine.position.move_vector(end_time, machine.velocity)
    #
    #     next_transmissions.append({'positions': {'start': start_pos, 'end': end_pos}, 'time': {'start': start_time, 'end': end_time}})
    #
    #     current_pos = next_transmissions[0]['positions']['end']
    #     while current_pos.x < self.vein.length:
    #         start_time = next_transmissions[-1]['time']['end'] + machine.idle_duration
    #         end_time = start_time + machine.transmission_duration
    #         if end_time > 6e7:
    #             break
    #         start_pos = machine.position.move_vector(start_time, machine.velocity)
    #         end_pos = machine.position.move_vector(end_time, machine.velocity)
    #         next_transmissions.append({'positions': {'start': start_pos, 'end': end_pos}, 'time': {'start': start_time, 'end': end_time}})
    #         current_pos = end_pos
    #
    #     # machine.next_transmissions = filter(lambda tr: tr['positions']['start'].distance_from_point(self.router.position) <= self.router.transmission_radius or tr['positions']['end'].distance_from_point(self.router.position) <= self.router.transmission_radius, next_transmissions)
    #
    #     return list(filter(lambda tr: tr['positions']['start'].distance_from_point(self.router.position) <= self.router.transmission_radius or tr['positions']['end'].distance_from_point(self.router.position) <= self.router.transmission_radius, next_transmissions))

    def get_successful_tr_and_collisions(self, machine: NanoNode):
        # collisions = []
        other_machines = [m for m in self.nano_machines if m != machine and {machine, m} not in self.collisions]
        transmissions_within_range = list(filter(lambda tr: tr['positions']['start'].distance_from_point(self.router.position) < self.router.transmission_radius and tr['positions']['end'].distance_from_point(self.router.position) < self.router.transmission_radius, machine.next_transmissions))
        for tr in transmissions_within_range:
            is_collisions_detected = False
            # if tr['positions']['start'].distance_from_point(self.router.position) and tr['positions']['end'].distance_from_point(self.router.position):
            for m in other_machines:
                if len(list(filter(lambda t: abs(t['time']['e_start'] - tr['time']['start']) < machine.transmission_duration, m.next_transmissions))):
                    self.logger.info(indent(f'machine.next_transmissions: {machine.next_transmissions}', 6))
                    self.logger.info(indent(f'other machine.next_transmissions: {m.next_transmissions}', 6))
                    self.logger.info(indent(f'There is collision between machine {str(machine)} and {str(m)}', 6))
                    is_collisions_detected = True
                    self.collisions.append({machine, m})
            if not is_collisions_detected:
                #TODO: co jesli wiecej niz jedna transmisja z powodzeniem
                machine.transmission_result = True

                # if sum(list(map(lambda other_tr: abs(other_tr['time']['start'] - tr['time']['start']) < machine.transmission_duration, all_transmissions))) == 1:
                #     machine.transmission_result = True
                # else:
                #     self.logger.info(indent(f'machine.next_transmissions: {machine.next_transmissions}', 6))
                #     self.logger.info(indent(f'There is collision during machine {str(machine)} transmission', 6))
                #     self.collisions += 1

    def run_simulation(self):
        self.logger.info(indent(f'{len(self.nano_machines)} machines are potential to transmit data data', 6))
        while self.testing_machines:
            for machine in list(self.testing_machines):
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

    def run_new_simulation(self):
        self.logger.info(indent(f'{len(self.nano_machines)} machines are potential to transmit data data', 6))
        ##new##
        # all_transmissions = []
        # for machine in self.nano_machines:
        #     machine.next_transmissions = self.next_transmissions(machine)
        #     all_transmissions = all_transmissions + machine.next_transmissions

            # self.logger.info(indent(f'machine.next_transmissions: {machine.next_transmissions}', 6))
        # self.logger.info(indent(f'all_transmissions: {all_transmissions}', 6))

        for machine in self.nano_machines:
            self.get_successful_tr_and_collisions(machine)
            # if len(machine.next_transmissions) >= 2:
                # self.logger.info(indent(f'machine.next_transmissions: {machine.next_transmissions}', 6))
                # self.logger.info(indent(f'machine.velocity: {machine.velocity}', 6))
                # vein_diameter_start = Vector(-1 * (self.vein.length / 2), 0, 0)
                # vein_diameter_end = Vector(self.vein.length / 2, 0, 0)
                # self.logger.info(indent(f'machine distance from diameter: {machine.position.distance_from_line(vein_diameter_start, vein_diameter_end)}', 6))
            ###new###
            # for tr in machine.next_transmissions:
            #     if tr['positions']['start'].distance_from_point(self.router.position) and tr['positions']['end'].distance_from_point(self.router.position):
            #         if sum(list(map(lambda other_tr: abs(other_tr['time']['start'] - tr['time']['start']) < machine.transmission_duration, all_transmissions))) == 1:
            #             machine.transmission_result = True
            #         else:
            #             self.logger.info(indent(f'machine.next_transmissions: {machine.next_transmissions}', 6))
            #             self.logger.info(indent(f'There is collision during machine {str(machine)} transmission', 6))
            #             self.collisions += 1

        self.failed_transmissions = len(list(filter(lambda m: not m.transmission_result, self.nano_machines)))
        self.successful_transmissions = len(list(filter(lambda m: m.transmission_result, self.nano_machines)))
        return self.successful_transmissions, self.failed_transmissions, len(self.collisions)
        # for m1 in self.nano_machines:
        #     for m1_next in m1.next_transmissions:
        #         for m2 in [m for m in self.nano_machines if m != m1]:
        #             for m2_next in m2.next_transmissions:
        #                 if abs(m1_next['time']['start'] - m2_next['time']['start']) <= m1.transmission_duration:
        #                     self.logger.info(indent(f'There is collision between machines {str(m1)} and {str(m2)}', 6))
        #                     self.collisions += 1
        #                     break
        #
        #
        #
        #
        # for machine in self.nano_machines:
        #     for tr in machine.next_transmissions:
        #         # if tr['positions']['start'].distance_from_point(self.router) and tr['positions']['end'].distance_from_point(self.router):
        #         for ref_machine in self.nano_machines:
        #             for ref_tr in ref_machine.
        #                 # if machine



        """
        1. iteruj po next transmissions i sprawdz czy któraś transmisja jest w całości w obszarze. Jeśli tak:
        2. sprawdź czy którakolwiek maszyna koliduje.
        3. ustaw transmission_rresult
        """
