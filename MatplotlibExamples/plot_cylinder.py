import matplotlib.pyplot as plt
import numpy as np
import pylab
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.animation as animation
from Vector import Vector
from mpl_toolkits.mplot3d import Axes3D
from time import sleep
from Veins.Vein import Vein
TIME_SAMPLE = 1
SIMULATION_TIME = 10**6
TRANSMISSION_DURATION = 64
IDLE_DURATION = 10**6
# cephalic_vein = Vein('Cephalic Vein', length=10.9, radius=0.3, velocity=1.09*10**(-5))

def draw_cylinder(length, radius, potential_machines, router, vein, df=None, sim_time=10**6):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # ax = p3.Axes3D(fig)
    title = ax.set_title('3D Test')
    # ax.set_xlim(left=-10, right=10)

    # Scatter graph

    # def update_graph(num):
    #     data = df[df['time'] == num]
    #     nodes._offsets3d = (data.x, data.y, data.z)
    #     title.set_text(f'3D Test, time={num}')
    # transmitting_machines = [machine for machine in all_devices.nano_nodes if machine.transmission_status['transmit'] is True]
    print(f'{len(potential_machines)} machines are potential to transmit data data')
    # print(f'{len(transmitting_machines)} machines are transmitting at the beginning of simulation')
    def update_graph(num):
        # for t in [TIME_SAMPLE * _ for _ in np.arange(0, int(SIMULATION_TIME / TIME_SAMPLE))]:
        #     # print(f'Current time: {t}')
        X = []
        Y = []
        Z = []
        X_tr = []
        Y_tr = []
        Z_tr = []

        for machine in potential_machines:
            machine.move(TIME_SAMPLE)
            if machine.position.x <= vein.length / 2:
                if machine.position.distance_from_point(router.position) <= router.transmission_radius:
                    machine.within_transmission_range = True
                    print(f'Machine {machine.device_id} is located within transmission range!')
                    print(machine)
                if machine.transmission_status['transmit']:
                    X_tr.append(machine.position.x)
                    Y_tr.append(machine.position.y)
                    Z_tr.append(machine.position.z)
                    if machine.transmission_timer > 0:
                        machine.transmission_timer -= 1
                    else:
                        if machine.transmission_status[
                            'started_within_transmission_range'] and machine.within_transmission_range:
                            if machine.transmission_result is None:
                                machine.transmission_result = True
                            print(f'Machine {machine.device_id} successfully sent data!')
                        # else:
                        machine.transmission_status = {'transmit': False,
                                                       'started_within_transmission_range': False}
                        machine.idle_timer = machine.idle_duration
                else:
                    X.append(machine.position.x)
                    Y.append(machine.position.y)
                    Z.append(machine.position.z)
                    if machine.idle_timer > 0:
                        machine.idle_timer -= 1
                    else:
                        if machine.within_transmission_range:
                            machine.transmission_status = {'transmit': True,
                                                           'started_within_transmission_range': True}
                            print(
                                f'Machine {machine.device_id} started to transmit data within transmission range!')
                        else:
                            machine.transmission_status = {'transmit': True,
                                                           'started_within_transmission_range': False}
                        machine.transmission_timer = machine.transmission_duration
            # machines_positions = np.append(machines_positions, [[machine.position.x, machine.position.y, machine.position.z]], axis=0)

            transiting_machines_within_range = [machine for machine in potential_machines if machine.within_transmission_range and machine.transmission_status['transmit'] is True]
            if len(transiting_machines_within_range) > 1:
                print(f'There is collision between machines {", ".join(str(m) for m in transiting_machines_within_range)}')
                for machine in transiting_machines_within_range:
                    machine.transmission_result = False

            # nodes._offsets3d = (data.x, data.y, data.z)
            nodes._offsets3d = (X, Y, Z)
            transmitting_nodes._offsets3d = (X_tr, Y_tr, Z_tr)
            title.set_text(f'3D Test, time={num}')

    X = [node.position.x for node in potential_machines if node.transmission_status['transmit'] is False]
    Y = [node.position.y for node in potential_machines if node.transmission_status['transmit'] is False]
    Z = [node.position.z for node in potential_machines if node.transmission_status['transmit'] is False]
    idle_labels = [node.velocity for node in potential_machines if node.transmission_status['transmit'] is False]

    X_tr = [node.position.x for node in potential_machines if node.transmission_status['transmit'] is True]
    Y_tr = [node.position.y for node in potential_machines if node.transmission_status['transmit'] is True]
    Z_tr = [node.position.z for node in potential_machines if node.transmission_status['transmit'] is True]
    # data = df[df['time'] == 0]
    # nodes = ax.scatter(data.x, data.y, data.z)
    nodes = ax.scatter(X, Y, Z, color='b')
    for i, velocity in enumerate([node.velocity for node in potential_machines if node.transmission_status['transmit'] is False]):
        ax.text(X[i], Y[i], Z[i], f'{velocity:0.4e}', size=10, zorder=1, color='k')
    transmitting_nodes = ax.scatter(X_tr, Y_tr, Z_tr, color='g')

    # nodes = ax.scatter(X, Y, Z)
    ax.scatter(router.position.x, router.position.y, router.position.z, c='r', marker='^')

    # Cylinder
    x = np.linspace(-length/2, length/2, 500)
    z = np.linspace(-radius, radius, 500)
    Xc, Zc = np.meshgrid(x, z)
    Yc = np.sqrt(radius**2-Zc**2)

    # Draw parameters
    rstride = 20
    cstride = 10
    ax.plot_surface(Xc, Yc, Zc, alpha=0.2, rstride=rstride, cstride=cstride)
    ax.plot_surface(Xc, -Yc, Zc, alpha=0.2, rstride=rstride, cstride=cstride)

    # Draw transmission area
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = router.transmission_radius * np.outer(np.cos(u), np.sin(v)) + router.position.x
    y = router.transmission_radius * np.outer(np.sin(u), np.sin(v)) + router.position.y
    z = router.transmission_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + router.position.z

    ax.plot_surface(x, y, z, color='r', alpha=0.2)
    # ax.(left=-10, right=10)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # ani = animation.FuncAnimation(fig, update_graph, sim_time, interval=1, blit=False)

    plt.show()

def update_points(num, nodes):
    pass


# print(np.random.uniform(1, 1, 10))