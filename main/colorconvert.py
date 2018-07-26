from math import pow

M = [[0.4124, 0.3576, 0.1805],
     [0.2126, 0.7152, 0.0722],
     [0.0193, 0.1192, 0.9505]]
D65 = [95.0429, 100.0, 108.8900]
chromaD65 = [0.3127, 0.3290, 100.0]


def rgb_xyz_old(rgb_vals):
    """Converts rgb values to the xyz color space."""
    for v in rgb_vals:
        v = v / 255
        if v <= 0.04045:
            v = v / 12.92
        else:
            v = ((v + 0.055) / 1.055) ** 2.4
        v *= 100
    return [sum((rgb_vals[j] * M[i][j] for j in range(3))) for i in range(3)]


def rgb_xyz(rgb):
    """Converts rgb values to the xyz color space."""
    vals = [(v / 3294.6 if v <= 10.31475 else pow(((v+14.025)/269.025), 2.4)) * 100 for v in rgb]
    return [sum((vals[j] * M[i][j] for j in range(3))) for i in range(3)]


def xyz_xyy(xyz_vals):
    """Converts xyz values to the xyY color space."""
    total = sum(xyz_vals)
    return [chromaD65[v] for v in range(3)] if total is 0 else [xyz_vals[i] / total for i in range(2)] + [xyz_vals[1]]


def rgb_xyy(rgb_vals):
    """Converts rgb values to the xyY color space."""
    return xyz_xyy(rgb_xyz([255, 255, 255] if rgb_vals == [0, 0, 0] else rgb_vals))


def rgb_xy(rgb_vals):
    """Converts rgb values to xy values for use with HUE lights."""
    return [round(x, 4) for x in rgb_xyy(rgb_vals)[:-1]]
