import requests
import re
import time
import csv
from pathlib import Path
from collections import Counter, OrderedDict
import colorconvert as cc
import lightcontrol as lc


class OrderedCounter(Counter, OrderedDict):
    """Counter that remembers the order elements are first encountered"""

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))

    def __reduce__(self):
        return self.__class__, (OrderedDict(self),)


config = Path('config/')

with open(config / "warningcolorconfig.csv") as f:
    COLOR_CODES = dict()
    lines = csv.reader(f)
    next(lines)
    UNKNOWN_XY = tuple(cc.rgb_xy([int(x) for x in next(lines)[1].split('-')]))
    STATUS_XY = tuple(cc.rgb_xy([255, 255, 0]))
    WHITE_XY = tuple(cc.rgb_xy([255, 255, 255]))
    for line_raw in lines:
        COLOR_CODES.update({line_raw[0]: tuple(cc.rgb_xy([int(x) for x in line_raw[1].split('-')]))})
    del lines


def request_info():
    with open(config / "networkconfig.csv") as f:
        lines = csv.reader(f)
        next(lines)
        line = next(lines)
        REQUEST_URL = line[0]
        REQUEST_AUTH = (line[1], line[2])
        del line, lines
        return REQUEST_URL, REQUEST_AUTH


def get_data():
    """
    Returns a dict representation of the network data.
    """
    info = request_info()
    return requests.get(info[0], auth=info[1]).json()


def color_counter():
    """
    Returns an OrderedCounter of colors in COLOR_CODES plus UNKNOWN_XY and STATUS_XY
    mapped to 0.
    """
    ret = {color: 0 for color in COLOR_CODES.values()}
    ret.update({UNKNOWN_XY: 0, STATUS_XY: 0})
    return OrderedCounter(ret)


def counted_colors():
    """
    Returns a dict of colors mapped to the amount of detected issues
    for their corresponding issue.
    """
    counter = color_counter()
    for address, stats in ((a, s) for a, s in get_data().items() if s['code'] != 1):
        code = stats['code']
        print('%s CODE %i' % (address, code))
        if code is 4:
            for regex, color in COLOR_CODES.items():
                if re.search(regex, address):
                    counter[color] += 1
                    break
            else:
                counter[UNKNOWN_XY] += 1
        elif code is 3:
            counter[STATUS_XY] += 1
    return counter


def check(colors=None):
    """
    Blinks all lights off in the correct color for every detected outage.

    :type colors: Counter
    """
    if colors is None:
        colors = counted_colors()
    elems = list(colors.elements())
    if len(elems) != 0:
        lc.set_all(bri=255)
    for i, color in enumerate(elems):
        if i is 0 or elems[i - 1] != color:
            lc.set_all(xy=color)
        lc.blink_off(1, wait=True)
    for color, amt in colors.items():
        if amt != 0:
            lc.set_all(xy=color)
            break
    else:
        lc.reset()


def looped_check(secs):
    """
    Checks network and blinks all lights off accordingly every secs seconds.

    :type secs: int
    """
    while True:
        check()
        time.sleep(secs)


def finite_looped_check(amt, secs):
    """
    Performs a network check and blinks all lights accordingly every secs seconds.
    Repeats amt times.

    :type amt: int
    :type secs: Any
    """
    for _ in range(amt):
        check()
        time.sleep(secs)


looped_check(10)
