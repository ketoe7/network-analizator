"""
    Copyright (C) 2020-2020
    Mikołaj Wierzbicki under thesis supervision of Paweł Kułakowski on behalf on AGH Academy of Science and Technology.
    All rights reserved

    History of Modification:
    Mikołaj Wierzbicki        Jul 31,  2020        Initial version
"""
from Devices.AllDevices import AllDevice
from Devices.NanoNode import NanoNode
from Devices.Router import Router
from Veins.Vein import Vein
from Vector import Vector
from datetime import datetime
import pandas as pd
import numpy as np
import os, errno
import random
import logging

"""All time variables are represented by micro-seconds!"""


# NANO_NODES_NUMBER = 100000
# NODES_WITHIN_CEPHALIC_VEIN = int(0.0056 * NANO_NODES_NUMBER)
TRANSMISSION_RADIUS_RANGE = 0.1
TIME_SAMPLE = 1
SIMULATION_TIME = 10**6
# SIMULATION_TIME = 60
# TRANSMISSION_DURATION = 10
TRANSMISSION_DURATION = 64
# IDLE_DURATION = 10
IDLE_DURATION = 10**6
# IDLE_DURATION = 2
# 60.6
cephalic_vein = Vein('Cephalic Vein', length=10.9, radius=0.3, velocity=1.09*10**(-5))
# cephalic_vein = Vein('Cephalic Vein', length=1, radius=0.3, velocity=1.09*10**(-2))


def print_and_return(sentence, f):
    print(sentence)
    f.write(sentence + '\n')
    return sentence + '\n'


def generate_data(nodes_within_cephalic_vein):
    all_devices = AllDevice()
    vein_diameter_start_point = Vector(-1*(cephalic_vein.length/2), 0, 0)
    vein_diameter_end_point = Vector(cephalic_vein.length/2, 0, 0)
    # router = Router(1, Vector(0, 0, cephalic_vein.radius), 0.1)
    router = Router(1, Vector((cephalic_vein.length/2)-TRANSMISSION_RADIUS_RANGE, 0, cephalic_vein.radius), TRANSMISSION_RADIUS_RANGE)
    # router = Router(1, Vector((cephalic_vein.length/2)-TRANSMISSION_RADIUS_RANGE, 0, 0), TRANSMISSION_RADIUS_RANGE)
    all_devices.add_device(router)
    dev_id = 1
    while len(all_devices.nano_nodes) < nodes_within_cephalic_vein:
        # x = random.uniform(-1*(cephalic_vein.length/2), cephalic_vein.length/2)

        x = random.uniform(-1*(cephalic_vein.length/2), router.position.x - router.transmission_radius)
        y = random.uniform(-1*cephalic_vein.radius, cephalic_vein.radius)
        z = random.uniform(-1*cephalic_vein.radius, cephalic_vein.radius)
        machine_position = Vector(x, y, z)
        distance_from_diameter = machine_position.distance(vein_diameter_start_point, vein_diameter_end_point)
        if distance_from_diameter < cephalic_vein.radius:
            vein_diameter = cephalic_vein.radius*2
            machine_velocity = cephalic_vein.velocity*2*(cephalic_vein.radius**2 - distance_from_diameter**2)/(cephalic_vein.radius**2)
            # machine_velocity = cephalic_vein.velocity
            transmit = random.choices([False, True], weights=(93.6, 6.4), k=1)
            # print(f'generated transmit parameter: {transmit[0]}')
            if transmit[0]:
                transmission_timer = random.choice(range(0,  TRANSMISSION_DURATION))
                idle_timer = IDLE_DURATION
            else:
                idle_timer = random.choice(range(0,  IDLE_DURATION))
                transmission_timer = TRANSMISSION_DURATION

            # router on the center
            # if (-1 * (router.transmission_radius) <= machine_position.y <= router.transmission_radius) and (-1 * router.transmission_radius <= machine_position.z <= router.transmission_radius):
            # router on the top
            if (-1 * (router.transmission_radius) <= machine_position.y <= router.transmission_radius) and (router.position.z - router.transmission_radius <= machine_position.z <= router.position.z + router.transmission_radius):
                transmission_result = None
            else:
                transmission_result = False

            all_devices.add_device(NanoNode(dev_id,
                                            machine_position,
                                            machine_velocity,
                                            transmission_status=(transmit[0], False),
                                            transmission_duration=TRANSMISSION_DURATION,
                                            transmission_timer=transmission_timer,
                                            idle_duration=IDLE_DURATION,
                                            idle_timer=idle_timer,
                                            transmission_result=transmission_result
                                            )
                                   )
            dev_id += 1

    return all_devices


def run_simulation():
    iter_number = 1000
    NANO_NODES_NUMBER = [30000, 40000]
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=f'./results/{NANO_NODES_NUMBER}_{iter_number:04}_iterations_router_on_top.txt',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    # current_time = 0
    # TODO: change for np.zeroes to improve efficiency
    machines_positions = np.empty([0, 3])

    final_results = {}
    logging.info(f'Simulation started. Parameters:')
    logging.info(f'NANO_NODES_NUMBER: {NANO_NODES_NUMBER}')
    logging.info(f'iter_number: {iter_number}\n')

    for number in NANO_NODES_NUMBER:
        log_path = f'./results/{number}_machines/'
        try:
            os.makedirs(log_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        handler = logging.FileHandler(os.path.join(log_path, f'{iter_number:04}_iterations_router_on_top.txt'), mode='w')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger(f'{number}_{iter_number}i_top')
        logger.addHandler(handler)

        logger.info(f'{" " * 2}{number} nano nodes\n')
        final_results[number] = {'transmissions': 0, 'collisions': 0}
        results_per_nano_nodes_number = []
        collisions_per_nano_nodes_number = []
        for _ in range(iter_number):
            logger.info(f'{" " * 4}{_ + 1} iteration')
            all_devices = generate_data(0.0056 * number)
            router = all_devices.router
            colisions = 0
            potential_machines = [machine for machine in all_devices.nano_nodes if machine.transmission_result is None]

            ##### Generate Collision #####

            # print(f'First 2 machines: {potential_machines[0].device_id} and {potential_machines[1].device_id}')
            # potential_machines[0].position = Vector(router.position.x - TRANSMISSION_RADIUS_RANGE + 0.01, router.position.y - TRANSMISSION_RADIUS_RANGE + 0.01, router.position.z - TRANSMISSION_RADIUS_RANGE + 0.01)
            # potential_machines[0].within_transmission_range = True
            # potential_machines[0].transmission_status['transmit'] = False
            # potential_machines[0].idle_timer = 1
            # potential_machines[0].transmission_timer = TRANSMISSION_DURATION
            # potential_machines[1].position = Vector(router.position.x - TRANSMISSION_RADIUS_RANGE + 0.02, router.position.y - TRANSMISSION_RADIUS_RANGE + 0.02, router.position.z - TRANSMISSION_RADIUS_RANGE + 0.02)
            # potential_machines[1].within_transmission_range = True
            # potential_machines[1].transmission_status['transmit'] = False
            # potential_machines[1].idle_timer = 2
            # potential_machines[1].transmission_timer = TRANSMISSION_DURATION

            ##### Generate Collision #####

            ##### Print potential machines #####
            # vein_diameter_start_point = Vector(-1 * (cephalic_vein.length / 2), 0, 0)
            # vein_diameter_end_point = Vector(cephalic_vein.length / 2, 0, 0)
            # for machine in potential_machines:
            #     logger.info(str(machine) + f', distance from diameter {machine.position.distance(vein_diameter_start_point, vein_diameter_end_point)}')
            # logger.info('\nrouter: ', str(router))

            ##### Print potential machines #####

            # timeline = np.array([np.ones(len(potential_machines)) * i for i in range(SIMULATION_TIME)]).flatten()
            # transmitting_machines = [machine for machine in potential_machines if machine.transmission_status['transmit'] is True]

            logger.info(f'{" " * 4}{len(potential_machines)} machines are potential to transmit data data')
            # print(f'{len(transmitting_machines)} of potential machines are transmitting at the beginning of simulation')

            for _ in [TIME_SAMPLE * _ for _ in np.arange(0, int(SIMULATION_TIME/TIME_SAMPLE))]:
                for machine in list(potential_machines):
                    if machine.position.x <= cephalic_vein.length/2 and machine.transmission_result is not False:
                        machine.move(TIME_SAMPLE)
                        if machine.position.distance_from_point(router.position) <= router.transmission_radius:
                            machine.within_transmission_range = True
                            # print(f'Machine {machine.device_id} is located within transmission range!')
                            # print(machine)
                        if machine.transmission_status['transmit']:
                            if machine.transmission_timer > 0:
                                machine.transmission_timer -= 1
                            else:
                                if machine.transmission_status['started_within_transmission_range'] and machine.within_transmission_range:
                                    if machine.transmission_result is None:
                                        machine.transmission_result = True
                                        logger.info(f'{" " * 8}Machine {machine.device_id} successfully sent data!')
                                # else:
                                machine.transmission_status = {'transmit': False, 'started_within_transmission_range': False}
                                machine.idle_timer = machine.idle_duration
                        else:
                            if machine.idle_timer > 0:
                                machine.idle_timer -= 1
                            else:
                                if machine.within_transmission_range:
                                    machine.transmission_status = {'transmit': True, 'started_within_transmission_range': True}
                                    # print(f'Machine {machine.device_id} started to transmit data within transmission range!')
                                else:
                                    machine.transmission_status = {'transmit': True, 'started_within_transmission_range': False}
                                machine.transmission_timer = machine.transmission_duration
                    else:
                        potential_machines.remove(machine)
                        # print(f'potential_machines: ' + f', '.join([m.device_id for m in potential_machines]))
                    # machines_positions = np.append(machines_positions, [[machine.position.x, machine.position.y, machine.position.z]], axis=0)

                transiting_machines_within_range = [machine for machine in potential_machines if machine.within_transmission_range and machine.transmission_status['transmit'] is True]
                if len(transiting_machines_within_range) > 1:
                    logger.info(f'{" " * 6}There is collision between machines {" and ".join(str(m) for m in transiting_machines_within_range)}')
                    for machine in transiting_machines_within_range:
                        machine.transmission_result = False
                    colisions += 1
                    # machines_positions = np.append(machines_positions, [[machine.position.x, machine.position.y, machine.position.z]], axis=0)

            failed_machines = 0
            success_machines = 0
            for machine in all_devices.nano_nodes:
                if machine.transmission_result not in [True, False]:
                    machine.transmission_result = False
                if machine.transmission_result:
                    success_machines += 1
                else:
                    failed_machines += 1
            rate = success_machines / len(all_devices.nano_nodes)
            logger.info(f'{" " * 4}{success_machines}/{len(all_devices.nano_nodes)} machines successfully sent data ({rate*100}%)')
            logger.info(f'{" " * 4}{colisions} collisions detected\n')
            # df = pd.DataFrame({"time": timeline, "x": machines_positions[:, 0], "y": machines_positions[:, 1], "z": machines_positions[:, 2]})
            # print(df[df['time']==5])
            # draw_cylinder(cephalic_vein.length, cephalic_vein.radius, all_devices.nano_nodes, router, df, SIMULATION_TIME)
            # draw_cylinder(cephalic_vein.length, cephalic_vein.radius, potential_machines, router, cephalic_vein, df=None, sim_time=SIMULATION_TIME)
            results_per_nano_nodes_number.append(success_machines)
            collisions_per_nano_nodes_number.append(colisions)

        logger.info(f'{" " * 2}Number of iterations: {iter_number}')
        logger.info(f'{" " * 2}Results for {number}: {results_per_nano_nodes_number}')
        count = len([i for i in results_per_nano_nodes_number if i > 0])
        logger.info(f'{" " * 2}The amount of successful transmissions: {count}')
        logger.info(f'{" " * 2}The amount of collisions: {colisions}')
        logger.info(f'{" " * 2}Rate: {count/iter_number*100}%\n')

        final_results[number]['transmissions'] = sum(results_per_nano_nodes_number)
        final_results[number]['collisions'] = sum(collisions_per_nano_nodes_number)

    logging.info(f'Amount of successful transmissions and collisions for {iter_number} iterations based on number of nano nodes:')
    for k, v in final_results.items():
        logging.info(f'{k} nano nodes: {v["transmissions"]} successful transmissions, {v["collisions"]} collisions')


        # f.write(log)


if __name__ == '__main__':
    # NODES_WITHIN_CEPHALIC_VEIN = int(0.0056 * 10000)
    # all_devices = generate_data(NODES_WITHIN_CEPHALIC_VEIN)
    # router = all_devices.router
    # potential_machines = [machine for machine in all_devices.nano_nodes if machine.transmission_result is None]
    # transmitting_machines = [machine for machine in potential_machines if machine.transmission_status['transmit'] is True]
    # print(f'{len(potential_machines)} machines are potential to transmit data data')
    # print(f'{len(transmitting_machines)} of potential machines are transmitting at the beginning of simulation')
    run_simulation()
    # draw_cylinder(cephalic_vein.length, cephalic_vein.radius, potential_machines, router, cephalic_vein, df=None, sim_time=SIMULATION_TIME)

