from Devices.NanoNode import NanoNode
from Devices.Router import Router
from Veins.Vein import Vein
from Vector import Vector
from utility import indent
from GeneralConfig import GeneralConfig
import random


class Simulator:
    def __init__(self, logger, nano_machines_amount, vein: Vein, mode, verbose, router_position='top', collision=False, const_speed=False):
        self.gc = GeneralConfig()
        self.vein = vein
        self.mode = mode
        self.verbose = verbose
        self.router = None
        self.nano_machines = []
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
                                 Vector((self.vein.length/2) - self.gc.transmission_radius_range, 0, self.vein.radius),
                                 self.gc.transmission_radius_range)
        elif router_position == 'center':
            self.router = Router(1,
                                 Vector((self.vein.length/2) - self.gc.transmission_radius_range, 0, 0),
                                 self.gc.transmission_radius_range)
        dev_id = 1
        counter = 0
        while counter < nodes_within_cephalic_vein:
            if collision and (counter == 0 or counter == 1):
                if counter == 0:
                    machine_position = Vector(self.router.position.x - self.gc.transmission_radius_range + 0.001,
                                              0,
                                              self.router.position.z - 0.001)
                else:
                    machine_position = Vector(self.router.position.x - self.gc.transmission_radius_range + 0.002,
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
                    machine_velocity = Vector.speed_for_d(self.vein.velocity, self.vein.radius, distance_from_diameter)
                    # machine_velocity = 2*self.vein.velocity*(self.vein.radius**2 - distance_from_diameter**2)/(self.vein.radius**2)
                if collision and (counter == 1 or counter == 2):
                    transmit = False
                    idle_timer = counter
                    transmission_timer = self.gc.transmission_duration
                else:
                    transmit = random.choices([False, True], weights=(93.6, 6.4), k=1)[0]
                    if transmit:
                        transmission_timer = random.choice(range(0, self.gc.transmission_duration))
                        idle_timer = self.gc.idle_duration
                    else:
                        idle_timer = random.choice(range(0, self.gc.idle_duration))
                        transmission_timer = self.gc.transmission_duration

                if collision and (counter == 1 or counter == 2):
                    print(machine_position.get_sphere_intersections(self.router.position, self.gc.transmission_radius_range))

                if machine_position.get_sphere_intersections(self.router.position, self.gc.transmission_radius_range):
                    self.nano_machines.append(NanoNode(dev_id,
                                                       machine_position,
                                                       machine_velocity,
                                                       is_transmitting=transmit,
                                                       started_within_transmission_range=False,
                                                       within_transmission_range=False,
                                                       transmission_timer=transmission_timer,
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
        return True

    def check(self, tr, i, prec=False):
        if tr['positions']['start'].distance_from_point(self.router.position) < self.router.transmission_radius \
                and tr['positions']['end'].distance_from_point(self.router.position) < self.router.transmission_radius:
            j = 1
            try:
                while abs(self.all_transmissions[i + j]['time']['e_start'] - tr['time']['start']) < self.gc.transmission_duration:
                    self.failed_transmissions.update({tr['id'], self.all_transmissions[i + j]["id"]})
                    self.collisions.append({tr["id"], self.all_transmissions[i + j]["id"]})
                    j += 1
            except IndexError:
                pass

            try:
                j = 1
                while abs(self.all_transmissions[i - j]['time']['e_end'] - tr['time']['end']) < self.gc.transmission_duration and i - j >= 0:
                    self.failed_transmissions.update({tr['id'], self.all_transmissions[i - j]["id"]})
                    self.collisions.append({tr["id"], self.all_transmissions[i - j]["id"]})
                    j += 1
            except IndexError:
                pass
            return False
        else:
            return True

    def run_new_simulation(self):
        if self.verbose:
            self.logger.info(indent(f'{len(self.nano_machines)} machines are potential to transmit data data', 6))
        self.all_transmissions = sorted([item for sublist in [m.next_transmissions for m in self.nano_machines] for item in sublist], key=lambda t: t['time']['e_start'])
        if self.verbose:
            self.logger.info(indent(f'{len(self.all_transmissions)} transmissions at least start within transmission area', 6))
            self.all_transmissions = sorted([t for t in self.nano_machines], key=lambda t: t['time']['e_start'])
            self.logger.info(self.all_transmissions)
        prec = False
        for i, tr in enumerate(self.all_transmissions):
            prec = self.check(tr, i, prec)
            if not prec:
                self.successful_receptions += 1
                self.successful_unique_receptions.update(tr['id'].split('_')[:-1])
                if tr['id'] not in self.failed_transmissions:
                    self.successful_transmissions += 1
                    self.successful_unique_transmissions.update(tr['id'].split('_')[:-1])
        if self.verbose:
            self.logger.info(indent(f'amount of successful transmissions if we do not take the collisions into account: {self.successful_receptions}', 6))
            self.logger.info(indent(f'successful transmissions: {self.successful_transmissions}', 6))
            self.logger.info(indent(f'collisions: {self.collisions}', 6))
            self.logger.info(indent(f'amount of failed transmissions which could be successful: {len(self.failed_transmissions)}', 6))
            self.logger.info(indent(f'failed transmissions which could be successful: {self.failed_transmissions}', 6))

            self.logger.info(indent(f'successful receptions: {self.successful_receptions}', 6))
            self.logger.info(indent(f'successful unique_receptions: {len(self.successful_unique_receptions)}', 6))
            self.logger.info(indent(f'successful unique_receptions: {self.successful_unique_receptions}', 6))
            self.logger.info(indent(f'successful transmissions: {self.successful_transmissions}', 6))
            self.logger.info(indent(f'successful unique transmissions: {len(self.successful_unique_transmissions)}', 6))
            self.logger.info(indent(f'successful unique transmissions: {self.successful_unique_transmissions}', 6))

        return self.successful_transmissions, len(self.nano_machines), len(self.collisions), self.successful_receptions, len(self.successful_unique_transmissions), len(self.successful_unique_receptions)


