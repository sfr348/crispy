
import numpy as np


def xy_to_psf(x, y, quad_cube):  # for odd image array width
    cx = quad_cube.shape[-1] // 2
    hw = (quad_cube.shape[-1] // 2 + 1)
    if x >= hw and y >= hw:  # in first quadrant
        s = (y - cx) * hw + (x - cx)
        return quad_cube[s]
    elif x < hw and y >= hw:  # second quadrant
        s = (y - cx) * hw + (cx - x - 1)
        return quad_cube[s, :, ::-1]
    elif x < hw and y < hw:  # third quadrant
        s = (cx - y - 1) * hw + (cx - x - 1)
        return quad_cube[s, ::-1, ::-1]
    else:                 # fourth quadrant
        s = (cx - y - 1) * hw + (x - cx)
        return quad_cube[s, ::-1, :]