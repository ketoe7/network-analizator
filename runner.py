from Simulator import Simulator
from Veins.Vein import Vein
import logging
import utility
from utility import indent
from datetime import datetime
import argparse


# nano_machines_amounts = [1]
# nano_machines_amounts = [1]
# iteration_number = 1000
cephalic_vein = Vein('Cephalic Vein', length=4.8, radius=0.3, velocity=1.09*10**(-5))
vein_for_one_machine_test = Vein('Short Vein', length=0.20002, radius=0.3, velocity=1.09*10**(-5))
transmission_radius_range = 0.1
time_sample = 1
simulation_time = 5*10**5
transmission_duration = 64
idle_duration = 10**6
# router_position = 'top'


def main(nano_machines_amounts, iteration_number, router_position, vein, collision):
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    common_logger = utility.get_common_logger(format='%(name)-12s: %(asctime)s %(levelname)-8s %(message)s',
                                              filename=f'./results/{nano_machines_amounts}_{iteration_number:04}_iterations_router_{router_position}_{now}.txt')
    final_results = {}
    results_per_nano_nodes_number = collisions_per_nano_nodes_number = []
    common_logger.info(f'Simulation started. Parameters:')
    common_logger.info(f'nano_machines_amounts: {nano_machines_amounts}')
    common_logger.info(f'iteration_number: {iteration_number}\n')

    for machines_amount in nano_machines_amounts:
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        logger = utility.get_logger(log_path=f'./results/{machines_amount}_machines/{iteration_number:04}_iterations_router_{router_position}_{now}.txt',
                                    level=logging.DEBUG,
                                    label=f'{machines_amount}_{iteration_number}i_{router_position}',
                                    formatter=logging.Formatter('%(name)-12s: %(asctime)s %(levelname)-8s %(message)s')
                                    )
        logger.info(indent(f'{machines_amount} nano nodes\n', 2))
        collisions = 0
        final_results[machines_amount] = {'transmissions': 0, 'collisions': 0}
        for _ in range(iteration_number):
            logger.info(indent(f'{_ + 1} iteration\n', 4))
            simulator = Simulator(iteration_number, logger, 0.0056*machines_amount, vein, transmission_radius_range,
                                  time_sample, simulation_time, transmission_duration, idle_duration, router_position, collision)
            success, failed, collisions = simulator.run_simulation()
            rate = success/(success+failed) if success+failed != 0 else 0
            logger.info(indent(f'{success}/{success+failed} machines successfully sent data ({rate*100:.2f}%)', 6))
            logger.info(indent(f'{collisions} collisions detected\n', 6))
            results_per_nano_nodes_number.append(success)
            collisions_per_nano_nodes_number.append(collisions)

        logger.info(indent(f'Number of iterations: {iteration_number}', 2))
        logger.info(indent(f'Results for {machines_amount}: {results_per_nano_nodes_number}', 2))
        logger.info(indent(f'The amount of successful transmissions: {sum(results_per_nano_nodes_number)}', 2))
        logger.info(indent(f'The amount of collisions: {collisions}', 2))
        successful_iterations = len(list(filter(lambda x: x>0, results_per_nano_nodes_number)))
        logger.info(indent(f'Successful iterations : {successful_iterations}/{iteration_number} ({successful_iterations/iteration_number*100:.4f}%)\n', 2))

        final_results[machines_amount]['transmissions'] = sum(results_per_nano_nodes_number)
        final_results[machines_amount]['collisions'] = sum(collisions_per_nano_nodes_number)
    common_logger.info(f'Amount of successful transmissions and collisions for {iteration_number} iterations based on number of nano nodes:')
    for k, v in final_results.items():
        common_logger.info(f'{k} nano nodes: {v["transmissions"]} successful transmissions, {v["collisions"]} collisions')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulation for nano communication system in human vascular system')
    parser.add_argument('-n', '--numbers', dest='numbers', type=int, nargs='+', required=True, help='The amounts of nano machines in vascular system')
    parser.add_argument('-i', '--iterations', dest='iterations', type=int, action='store', default=1000, help='Number of iterations')
    parser.add_argument('-p', '--position', dest='position', action='store', default='top', help='position of router ("top" and "center" available)')
    parser.add_argument('-v', '--vein', dest='vein', action='store', default='cephalic', help='Vein for simulation ("cephalic" and "short" available)')
    parser.add_argument('-c', '--collision', dest='collision', action='store_true', help='Generate collision')
    args = parser.parse_args()
    if args.vein == 'cephalic':
        vein = cephalic_vein
    elif args.vein == 'short':
        vein = vein_for_one_machine_test
    else:
        raise NameError('Only "cephalic" and "short" veins are available!')
    main(args.numbers, args.iterations, args.position, vein, args.collision)


