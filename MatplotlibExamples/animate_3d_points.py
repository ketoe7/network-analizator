from matplotlib import pyplot as plt
import numpy as np
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation

fig = plt.figure()
ax = p3.Axes3D(fig)

# create the parametric curve
t=np.arange(0, 2*np.pi, 2*np.pi/100)
x=np.cos(t)
y=np.sin(t)
z=t/(2.*np.pi)

# Scatter graph
X = [x[5], x[10], x[15]]
Y = [y[5], y[10], y[15]]
Z = [z[5], z[10], z[15]]
nodes = ax.scatter(X, Y, Z)
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])


# create the first plot
point, = ax.plot([x[0]], [y[0]], [z[0]], 'o')
point2, = ax.plot([x[-1]], [y[-1]], [z[-1]], 'o')
line, = ax.plot(x, y, z, label='parametric curve')
ax.legend()
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])


# second option - move the point position at every frame
def update_point(n, x, y, z, point, point2, nodes):
    # point.set_data(np.array([x[n], y[n]]))
    # point.set_3d_properties(z[n], 'z')
    # point2.set_data(np.array([x[-n], y[-n]]))
    # point2.set_3d_properties(z[-n], 'z')
    nodes.set_data(np.array([ [x[n]] for x in X ]))
    return point, point2


ani = animation.FuncAnimation(fig, update_point, 99, fargs=(x, y, z, point, point2))

plt.show()
