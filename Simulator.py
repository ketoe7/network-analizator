from Devices.NanoNode import NanoNode
from Devices.Router import Router
from Veins.Vein import Vein
from Vector import Vector
from utility import indent
import random


def move_wrapper(machine, vein, time_sample, router, testing_machines):
    if machine.position.x <= vein.length / 2 and not machine.transmission_result:
        machine.move(time_sample, router)
    else:
        testing_machines.remove(machine)
    return machine.device_id


class Simulator:
    def __init__(self, iteration_number, logger, nano_machines_amount, vein: Vein, mode, transmission_radius_range=0.1,
                 time_sample=1, simulation_time=10**6, transmission_duration=64, idle_duration=10**6,
                 router_position='top', collision=False, verbose=False, const_speed=False):
        self.iteration_number = iteration_number
        self.simulation_time = simulation_time
        self.transmission_radius_range = transmission_radius_range
        self.time_sample = time_sample
        self.transmission_duration = transmission_duration
        self.idle_duration = idle_duration
        self.potential_machines = []
        self.vein = vein
        self.mode = mode
        self.router = None
        self.nano_machines = []
        self.testing_machines = []
        self.collisions = []
        self.verbose = verbose
        self.logger = logger
        # self.collisions = 0
        self.all_transmissions = []
        self.failed_transmissions = set()
        self.successful_unique_transmissions = set()
        self.successful_unique_receptions = set()
        self.successful_transmissions = 0
        self.successful_receptions = 0
        self.const_speed = const_speed
        self.generate_data(nano_machines_amount, router_position, collision)

    def generate_data(self, nodes_within_cephalic_vein, router_position, collision):
        vein_diameter_start = Vector(-1 * (self.vein.length / 2), 0, 0)
        vein_diameter_end = Vector(self.vein.length / 2, 0, 0)
        if router_position == 'top':
            self.router = Router(1,
                                 Vector((self.vein.length/2) - self.transmission_radius_range, 0, self.vein.radius),
                                 self.transmission_radius_range)
        elif router_position == 'center':
            self.router = Router(1,
                                 Vector((self.vein.length/2) - self.transmission_radius_range, 0, 0),
                                 self.transmission_radius_range)
        dev_id = 1
        counter = 0
        while counter < nodes_within_cephalic_vein:
            if collision and (counter == 0 or counter == 1):
                if counter == 0:
                    machine_position = Vector(self.router.position.x - self.transmission_radius_range + 0.001,
                                              0,
                                              self.router.position.z - 0.001)
                else:
                    machine_position = Vector(self.router.position.x - self.transmission_radius_range + 0.002,
                                              0,
                                              self.router.position.z - 0.002)

            else:
                x = random.uniform(-1 * (self.vein.length / 2), self.router.position.x - self.router.transmission_radius)
                y = random.uniform(-1 * self.vein.radius, self.vein.radius)
                z = random.uniform(-1 * self.vein.radius, self.vein.radius)
                machine_position = Vector(x, y, z)
            distance_from_diameter = machine_position.distance_from_line(vein_diameter_start, vein_diameter_end)
            if distance_from_diameter < self.vein.radius - 0.00001:
                counter += 1
                if self.const_speed:
                    machine_velocity = self.vein.velocity
                else:
                    machine_velocity = 2*self.vein.velocity*(self.vein.radius**2 - distance_from_diameter**2)/(self.vein.radius**2)
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
        return True

    def remove_nano_machine(self, machine):
        self.nano_machines.remove(machine)

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

    def check(self, tr, i, prec=False):
        if tr['positions']['start'].distance_from_point(self.router.position) < self.router.transmission_radius and tr['positions']['end'].distance_from_point(self.router.position) < self.router.transmission_radius:
            j = 1
            try:
                while abs(self.all_transmissions[i + j]['time']['e_start'] - tr['time']['start']) < self.transmission_duration:
                    self.failed_transmissions.update({tr['id'], self.all_transmissions[i + j]["id"]})
                    self.collisions.append({tr["id"], self.all_transmissions[i + j]["id"]})
                    j += 1
            except IndexError:
                pass

            try:
                j = 1
                while abs(self.all_transmissions[i - j]['time']['e_end'] - tr['time']['end']) < self.transmission_duration and i - j >= 0:
                    self.failed_transmissions.update({tr['id'], self.all_transmissions[i - j]["id"]})
                    self.collisions.append({tr["id"], self.all_transmissions[i - j]["id"]})
                    j += 1
            except IndexError:
                pass
            return False
        else:
            return True

    def run_new_simulation(self):
        # self.logger.info(indent(f'{len(self.nano_machines)} machines are potential to transmit data data', 6))
        # self.all_transmissions = list(itertools.chain.from_iterable([m.next_transmissions for m in self.nano_machines]))
        self.all_transmissions = sorted([item for sublist in [m.next_transmissions for m in self.nano_machines] for item in sublist], key=lambda t: t['time']['e_start'])
        # self.logger.info(indent(f'{len(self.all_transmissions)} transmissions at least start within transmission area', 6))
        # self.all_transmissions = sorted([t for t in self.nano_machines], key=lambda t: t['time']['e_start'])
        # self.logger.info(self.all_transmissions)
        prec = False
        for i, tr in enumerate(self.all_transmissions):
            prec = self.check(tr, i, prec)
            if not prec:
                self.successful_receptions += 1
                self.successful_unique_receptions.update(tr['id'].split('_')[:-1])
                if tr['id'] not in self.failed_transmissions:
                    self.successful_transmissions += 1
                    self.successful_unique_transmissions.update(tr['id'].split('_')[:-1])
        # self.logger.info(indent(f'amount of successful transmissions if we do not take the collisions into account: {self.successful_receptions}', 6))
        # self.logger.info(indent(f'successful transmissions: {self.successful_transmissions}', 6))
        # self.logger.info(indent(f'collisions: {self.collisions}', 6))
        # self.logger.info(indent(f'amount of failed transmissions which could be successful: {len(self.failed_transmissions)}', 6))
        # self.logger.info(indent(f'failed transmissions which could be successful: {self.failed_transmissions}', 6))

        # self.logger.info(indent(f'successful receptions: {self.successful_receptions}', 6))
        # self.logger.info(indent(f'successful unique_receptions: {len(self.successful_unique_receptions)}', 6))
        # self.logger.info(indent(f'successful unique_receptions: {self.successful_unique_receptions}', 6))
        # self.logger.info(indent(f'successful transmissions: {self.successful_transmissions}', 6))
        # self.logger.info(indent(f'successful unique transmissions: {len(self.successful_unique_transmissions)}', 6))
        # self.logger.info(indent(f'successful unique transmissions: {self.successful_unique_transmissions}', 6))

        return self.successful_transmissions, len(self.nano_machines), len(self.collisions), self.successful_receptions, len(self.successful_unique_transmissions), len(self.successful_unique_receptions)






            # if tr['positions']['start'].distance_from_point(self.router.position) < self.router.transmission_radius and tr['positions']['end'].distance_from_point(self.router.position) < self.router.transmission_radius:
            #     # is_collisions_detected = False
            #     # pom = set()
            #     # try:
            #     j = 1
            #     while True:
            #         # pom.update({tr['id'], self.all_transmissions[i+j]['id']})
            #         # self.logger.info(indent(f'machine transmission: {tr}', 6))
            #         # self.logger.info(indent(f'other machine.next_transmissions: {self.all_transmissions[i+1]}', 6))
            #         # self.logger.info(indent(f'There is collision between machine {tr["id"]} and {self.all_transmissions[i+1]["id"]}', 6))
            #         # is_collisions_detected = True
            #         can_continue = False
            #         try:
            #             if abs(self.all_transmissions[i+j]['time']['e_start'] - tr['time']['start']) < self.transmission_duration:
            #                 can_continue = True
            #                 self.failed_transmissions.update({tr['id'], self.all_transmissions[i + j]["id"]})
            #                 self.collisions.append({tr["id"], self.all_transmissions[i+j]["id"]})
            #                 # if abs(self.all_transmissions[i - j]['time']['e_start'] - tr['time']['start']) < self.transmission_duration:
            #                 #     self.failed_transmissions.update({tr['id'], self.all_transmissions[i - j]["id"]})
            #                 #     self.collisions.append({tr["id"], self.all_transmissions[i - j]["id"]})
            #                 # j += 1
            #                 # continue
            #         except IndexError:
            #             pass
            #
            #         if abs(self.all_transmissions[i-j]['time']['e_start'] - tr['time']['start']) < self.transmission_duration and i-j > 0:
            #             can_continue = True
            #             self.failed_transmissions.update({tr['id'], self.all_transmissions[i-j]["id"]})
            #             self.collisions.append({tr["id"], self.all_transmissions[i-j]["id"]})
            #
            #         if can_continue:
            #             j += 1
            #         else:
            #             break

                    # elif abs(self.all_transmissions[i - j]['time']['e_start'] - tr['time']['start']) < self.transmission_duration:
                    #     self.failed_transmissions.update({tr['id'], self.all_transmissions[i - j]["id"]})
                    #     self.collisions.append({tr["id"], self.all_transmissions[i - j]["id"]})
                    #     j += 1
                    #     continue
                    # else:
                    #     break
                # except IndexError:
                #     pass
                # finally:
                #     if pom:
                #         self.logger.info(indent(f'There is collision between machines {", ".join(pom)}', 6))# {tr["id"]} and {self.all_transmissions[i + 1]["id"]}',6))
                #         # self.failed_transmissions.update(pom)
                #         # self.collisions.append(pom)
        #         if tr['id'] not in self.failed_transmissions:
        #             self.successful_transmissions += 1
        # return self.successful_transmissions, len(self.nano_machines), len(self.collisions)





        # for machine in self.nano_machines:
        #     self.get_successful_tr_and_collisions(machine)
        #
        # self.failed_transmissions = len(list(filter(lambda m: not m.transmission_result, self.nano_machines)))
        # self.successful_transmissions = len(list(filter(lambda m: m.transmission_result, self.nano_machines)))
        # return self.successful_transmissions, self.failed_transmissions, len(self.collisions)

