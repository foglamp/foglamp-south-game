# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Module for IoT Lab Game 'poll' type plugin """

import copy
import json
import uuid
import logging

from foglamp.common import logger
from foglamp.plugins.common import utils

_LOGGER = logger.setup(__name__, level=logging.INFO)

try:
    from envirophat import light, weather, motion       # unused: analog
except FileNotFoundError:
    _LOGGER.error("Ensure i2c is enabled on the Pi and other dependencies are installed correctly!")


__author__ = "Mark Riddoch"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Enviro pHAT Poll Plugin',
        'type': 'string',
        'default': 'game',
        'readonly': 'true'
    }
}

_LIGHT_THRESHOLD = 40
_MAGNETOMETER_THRESHOLD = 100

_RED_POINTS = 1.0
_GREEN_POINTS = 2.0
_BLUE_POINTS = 3.0
_LINEAR_FACTOR = 0.1
_LATERAL_FACTOR = 0.3
_FLIP_PENALTY = -10.0

state = {}


def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'IoT Lab Game Plugin',
        'version': '1.7.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.
    Args:
        config: JSON configuration document for the South service configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """
    data = copy.deepcopy(config)
    magnetometer = motion.magnetometer()
    state["magx"] = magnetometer[0]
    state["magy"] = magnetometer[1]
    state["magz"] = magnetometer[2]
    state["light"] = "white"
    state["inverted"] = "No"
    return data


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.
    Available for poll mode only.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        Exception
    """

    time_stamp = utils.local_timestamp()
    data = list()

    try:
        moving = False
        rgb = light.rgb()
        magnetometer = motion.magnetometer()
        if abs(magnetometer[0] - state["magx"]) > _MAGNETOMETER_THRESHOLD:
            moving = True
        state["magx"] = magnetometer[0]
        state["magy"] = magnetometer[1]
        state["magz"] = magnetometer[2]
        accelerometer = [round(x, 1) for x in motion.accelerometer()]
        if moving and state["light"] != "red" and rgb[0] > rgb[1] + _LIGHT_THRESHOLD and rgb[0] > rgb[2] + _LIGHT_THRESHOLD:
            data.append({
                'asset': 'game/points',
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "red": _RED_POINTS,
                    "green": 0.0,
                    "blue": 0.0,
                    "accelerometer": 0.0,
                    "lateral": 0.0,
                    "flip": 0.0
                }
            })
            state["light"] = "red"
            leds.on()
        elif moving and state["light"] != "green" and rgb[1] > rgb[0] + _LIGHT_THRESHOLD and rgb[1] > rgb[2] + _LIGHT_THRESHOLD:
            data.append({
                'asset': 'game/points',
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "red": 0.0,
                    "green": _GREEN_POINTS,
                    "blue": 0.0,
                    "accelerometer": 0.0,
                    "lateral": 0.0,
                    "flip": 0.0
                }
            })
            state["light"] = "green"
            leds.on()
        elif moving and state["light"] != "blue" and rgb[2] > rgb[0] + _LIGHT_THRESHOLD and rgb[2] > rgb[1] + _LIGHT_THRESHOLD:
            data.append({
                'asset': 'game/points',
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": _BLUE_POINTS,
                    "accelerometer": 0.0,
                    "lateral": 0.0,
                    "flip": 0.0
                }
            })
            state["light"] = "blue"
            leds.on()
        elif moving:
            state["light"] = "white"
            leds.off()
        if abs(accelerometer[0]) > 0.1:
            data.append({
                'asset': 'game/points',
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0,
                    "accelerometer": abs(accelerometer[0] * _LINEAR_FACTOR),
                    "lateral": 0.0,
                    "flip": 0.0
                }
            })
        if abs(accelerometer[1]) > 0.1:
            data.append({
                'asset': 'game/points',
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0,
                    "accelerometer": 0.0,
                    "lateral": abs(accelerometer[1] * _LATERAL_FACTOR),
                    "flip": 0.0
                }
            })
        if state["inverted"] == "No" and accelerometer[2] < -0.2:
            data.append({
                'asset': 'game/points',
                'timestamp': time_stamp,
                'key': str(uuid.uuid4()),
                'readings': {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0,
                    "accelerometer": 0.0,
                    "lateral": 0.0,
                    "flip": _FLIP_PENALTY
                }
            })
            state["inverted"] = "Yes"
        elif accelerometer[2] > 0.2:
            state["inverted"] = "No"
    except (Exception, RuntimeError) as ex:
        _LOGGER.exception("IoT Lab Game exception: {}".format(str(ex)))
        raise ex
    else:
        _LOGGER.debug("IoT Lab Game reading: {}".format(json.dumps(data)))
        return data


def plugin_reconfigure(handle, new_config):
    """  Reconfigures the plugin
    it should be called when the configuration of the plugin is changed during the operation of the South service;
    The new configuration category should be passed.
    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info("Old config for Iot Lab Game plugin {} \n new config {}".format(handle, new_config))
    new_handle = copy.deepcopy(new_config)
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the South service being shut down.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info('IoT Lab Game poll plugin shut down.')
