from Simulator import Simulator
from Veins.Vein import Vein
import logging
import utility
from utility import indent
from datetime import datetime
import argparse
import math
import numpy as np


# nano_machines_amounts = [1]
# nano_machines_amounts = [1]
# iteration_number = 1000
# cephalic_vein = Vein('Cephalic Vein', length=4.8, radius=0.3, velocity=1.09*10**(-5))
cephalic_vein = Vein('Cephalic Vein', length=726.67, radius=0.3, velocity=1.09*10**(-5))
vein_for_one_machine_test = Vein('Short Vein', length=0.20002, radius=0.3, velocity=1.09*10**(-5))
transmission_radius_range = 0.1
time_sample = 1
simulation_time = 6e7
transmission_duration = 64
idle_duration = 10**6
# router_position = 'top'


def main(nano_machines_amounts, iteration_number, router_position, vein, collision, mode, const_speed=False):
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    common_logger = utility.get_common_logger(format='%(name)-12s: %(asctime)s %(levelname)-8s %(message)s',
                                              filename=f'./results/{nano_machines_amounts}_{iteration_number:04}_iterations_router_{router_position}_{now}.txt')
    final_results = {}
    # print(f'initial transmissions_per_nano_nodes_number: {transmissions_per_nano_nodes_number}')
    common_logger.info(f'Simulation started. Parameters:')
    common_logger.info(f'nano_machines_amounts: {nano_machines_amounts}')
    common_logger.info(f'iteration_number: {iteration_number}\n')

    for machines_amount in nano_machines_amounts:
        transmissions_per_nano_nodes_number = []
        unique_transmissions_per_nano_nodes_number = []
        receptions_per_nano_nodes_number = []
        unique_receptions_per_nano_nodes_number = []
        collisions_per_nano_nodes_number = []

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        logger = utility.get_logger(log_path=f'./results/{machines_amount}_machines/{iteration_number:04}_iterations_router_{router_position}_{now}.txt',
                                    level=logging.DEBUG,
                                    label=f'{machines_amount}_{iteration_number}i_{router_position}',
                                    formatter=logging.Formatter('%(name)-12s: %(asctime)s %(levelname)-8s %(message)s')
                                    )
        logger.info(indent(f'{machines_amount} nano nodes\n', 2))
        collisions = 0
        final_results[machines_amount] = {'transmissions': 0, 'collisions': 0}
        if vein.name == 'Short Vein':
            machines_in_vein_amount = machines_amount
        else:
            machines_in_vein_amount = int(machines_amount * (math.pi * 0.3**2 * vein.length)/5000)
        for _ in range(iteration_number):
            # print(f'_ for {_} time')
            # logger.info(indent(f'{_ + 1} iteration', 4))

            # simulator = Simulator(iteration_number, logger, machines_in_vein_amount, vein, transmission_radius_range,
            #                       time_sample, simulation_time, transmission_duration, idle_duration, router_position, collision)

            simulator = Simulator(iteration_number=iteration_number,
                                  logger=logger,
                                  nano_machines_amount=machines_in_vein_amount,
                                  vein=vein,
                                  mode=mode,
                                  transmission_radius_range=transmission_radius_range,
                                  time_sample=time_sample,
                                  simulation_time=simulation_time,
                                  transmission_duration=transmission_duration,
                                  idle_duration=idle_duration,
                                  router_position=router_position,
                                  collision=collision,
                                  const_speed=const_speed
                                  )

            # simulator = Simulator(iteration_number, logger, 0.0056*machines_amount*vein.length/(60*vein.velocity*10**6), vein, transmission_radius_range,
            #                       time_sample, simulation_time, transmission_duration, idle_duration, router_position,
            #                       collision)
            # simulator = Simulator(iteration_number, logger, machines_amount, vein,
            #                       transmission_radius_range,
            #                       time_sample, simulation_time, transmission_duration, idle_duration, router_position,
            #                       collision)
            # tr, failed, collisions = simulator.run_new_simulation()
            tr, all_machines, collisions, receptions, unique_tr, unique_receptions = simulator.run_new_simulation()

            # rate = tr/(tr+failed) if tr+failed != 0 else 0
            # logger.info(indent(f'{tr}/{tr+failed} machines successfully sent data ({rate*100:.2f}%)', 6))

            rate = tr / all_machines if all_machines != 0 else 0
            # logger.info(indent(f'{tr} successful transmissions per {all_machines} potentials machines ({rate * 100:.2f}%)', 6))
            # logger.info(indent(f'{collisions} collisions detected', 6))
            transmissions_per_nano_nodes_number.append(tr)
            unique_transmissions_per_nano_nodes_number.append(unique_tr)
            receptions_per_nano_nodes_number.append(receptions)
            unique_receptions_per_nano_nodes_number.append(unique_receptions)
            collisions_per_nano_nodes_number.append(collisions)

        logger.info(indent(f'Number of iterations: {iteration_number}', 2))
        logger.info(indent(f'machines_in_vein_amount: {machines_in_vein_amount}\n', 2))
        # logger.info(indent(f'Results for {machines_amount}: {transmissions_per_nano_nodes_number}', 2))
        logger.info(indent(f'The amount of successful receptions: {sum(receptions_per_nano_nodes_number)}', 2))
        logger.info(indent(f'The amount of successful unique receptions: {sum(unique_receptions_per_nano_nodes_number)}', 2))
        logger.info(indent(f'The amount of successful transmissions: {sum(transmissions_per_nano_nodes_number)}', 2))
        logger.info(indent(f'The amount of successful unique transmissions: {sum(unique_transmissions_per_nano_nodes_number)}', 2))
        logger.info(indent(f'The amount of collisions: {sum(collisions_per_nano_nodes_number)}', 2))
        logger.info(indent(f'Average amount of receptions per minute for {machines_amount} nano machines: {sum(receptions_per_nano_nodes_number)/iteration_number} (standard deviation: {np.std(receptions_per_nano_nodes_number)})', 2))
        logger.info(indent(f'Average amount of unique receptions per minute for {machines_amount} nano machines: {sum(unique_receptions_per_nano_nodes_number)/iteration_number} (standard deviation: {np.std(unique_receptions_per_nano_nodes_number)})', 2))
        logger.info(indent(f'Average amount of transmissions per minute for {machines_amount} nano machines: {sum(transmissions_per_nano_nodes_number)/iteration_number} (standard deviation: {np.std(transmissions_per_nano_nodes_number)})', 2))
        logger.info(indent(f'Average amount of unique transmissions per minute for {machines_amount} nano machines: {sum(unique_transmissions_per_nano_nodes_number)/iteration_number} (standard deviation: {np.std(unique_transmissions_per_nano_nodes_number)})', 2))
        logger.info(indent(f'Average amount of collisions per minute for {machines_amount} nano machines: {sum(collisions_per_nano_nodes_number)/iteration_number}', 2))
        successful_iterations = len(list(filter(lambda x: x > 0, transmissions_per_nano_nodes_number)))
        logger.info(indent(f'Successful iterations : {successful_iterations}/{iteration_number} ({successful_iterations/iteration_number*100:.4f}%)\n', 2))

        final_results[machines_amount]['transmissions'] = sum(transmissions_per_nano_nodes_number)
        final_results[machines_amount]['unique_transmissions'] = sum(unique_transmissions_per_nano_nodes_number)
        final_results[machines_amount]['collisions'] = sum(collisions_per_nano_nodes_number)
        final_results[machines_amount]['receptions'] = sum(receptions_per_nano_nodes_number)
        final_results[machines_amount]['unique_receptions'] = sum(unique_receptions_per_nano_nodes_number)
    common_logger.info(f'Amount of successful transmissions, collisions and receptions for {iteration_number} iterations based on number of nano nodes:')
    for k, v in final_results.items():
        common_logger.info(f'{k} nano nodes: {v["receptions"]} receptions, {v["unique_receptions"]} unique_receptions, {v["transmissions"]} successful transmissions, {v["unique_transmissions"]} successful unique_transmissions, {v["collisions"]} collisions')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulation for nano communication system in human vascular system')
    parser.add_argument('-n', '--numbers', dest='numbers', type=int, nargs='+', required=True, help='The amounts of nano machines in vascular system')
    parser.add_argument('-i', '--iterations', dest='iterations', type=int, action='store', default=1000, help='Number of iterations')
    parser.add_argument('-p', '--position', dest='position', action='store', default='top', help='position of router ("top" and "center" available)')
    parser.add_argument('-v', '--vein', dest='vein', action='store', default='cephalic', help='Vein for simulation ("cephalic" and "short" available)')
    parser.add_argument('-c', '--collision', dest='collision', action='store_true', help='Generate collision')
    parser.add_argument('-m', '--mode', dest='mode', choices=['receive', 'transmit'], action='store', default='receive', help='Mode of the simulation ("receive" and "transmit" available')
    parser.add_argument('--const_speed', dest='const_speed', action='store_true', help='Constant speed of machines')
    args = parser.parse_args()
    if args.vein == 'cephalic':
        radius = 0.3
        velocity_avg = 1.09 * 10 ** (-5)
        biggest_velocity = velocity_avg*2*(radius**2-(radius - transmission_radius_range)**2)/(radius ** 2)
        abstract_vein_length = simulation_time * biggest_velocity
        print(f'abstract_vein_length: {abstract_vein_length}')
        real_length = 4.8
        # 726.67
        vein = Vein('Cephalic Vein', length=abstract_vein_length, radius=radius, velocity=velocity_avg)
    elif args.vein == 'short':
        vein = Vein('Short Vein', length=0.20002, radius=0.3, velocity=1.09*10**(-5))
    else:
        raise NameError('Only "cephalic" and "short" veins are available!')
    # print(args.iterations)
    print(f'args.collision: {args.collision}')
    main(args.numbers, args.iterations, args.position, vein, args.collision, args.mode, args.const_speed)
