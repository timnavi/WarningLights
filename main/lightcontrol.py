import requests
import time
from pathlib import Path
import csv
import colorconvert as cc
import json as js
from collections import defaultdict

config = Path('config')

with open(config / "bridgeconfig.csv") as f:
    BRIDGES = defaultdict()
    reader = csv.reader(f)
    next(reader)
    for line in reader:
        br_url = 'http://%s/api/%s/lights' % tuple(line)
        BRIDGES[line[0]] = {i: "%s/%i/state" % (br_url, i) for i in range(1, len(requests.get(br_url).json()) + 1)}
    del reader

with open(config / "customcolorsettings.json") as f:
    data = js.load(f)
    DEFAULT_XY = cc.rgb_xy(data['default']['rgb'])
    DEFAULT_BRI = int(data['default']['bri'])
    CUSTOM_SETTINGS = data['custom']
    del data


def reset():
    """
    Resets lights to custom settings.
    """
    for ip, lights in BRIDGES.items():
        for light, url in lights.items():
            if ip in CUSTOM_SETTINGS.keys() and str(light) in CUSTOM_SETTINGS[ip].keys():
                command = defaultdict()
                settings = CUSTOM_SETTINGS[ip][str(light)]
                if 'rgb' in settings.keys():
                    command['xy'] = cc.rgb_xy(settings['rgb'])
                    del settings['rgb']
                for k, v in settings.items():
                    command[k] = v
                set_light(url, json=command)
            else:
                set_light(url, xy=DEFAULT_XY, bri=DEFAULT_BRI)


def set_light(url, json=None, **kwargs):
    """
    Sends command to desired light.

    :type url: str
    :type json: dict
    :type kwargs: Any
    """
    if json is None:
        json = {}
    json.update(kwargs)
    requests.put(url, json=json)


def set_all(json=None, **kwargs):
    """
    Sends command to all lights in BRIDGES.

    :type json: dict
    :type kwargs: Any
    """
    if json is None:
        json = {}
    json.update(kwargs)
    for bridge in BRIDGES.values():
        for url in bridge.values():
            set_light(url, json=json)


def blink_off(secs, wait=False):
    """
    All lights blink off once for secs seconds.\n
    Waits an additional secs seconds after executing if
    wait is True.

    :type secs: int
    :type wait: bool
    """
    set_all(on=False)
    time.sleep(secs)
    set_all(on=True)
    if wait:
        time.sleep(secs)
