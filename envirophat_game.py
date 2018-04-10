# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Module for IoT Lab Game 'poll' type plugin """

import copy
import datetime
import json
import uuid
from envirophat import light, weather, motion, analog

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions


__author__ = "Mark Riddoch"
__copyright__ = "Copyright (c) 2018 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
         'description': 'Enviro pHAT Poll Plugin',
         'type': 'string',
         'default': 'envirophat'
    },
    'pollInterval': {
        'description': 'The interval between poll calls to the South device poll routine expressed in milliseconds.',
        'type': 'integer',
        'default': '100'
    },
}

_LOGGER = logger.setup(__name__, level=20)

_LIGHT_THRESHOLD = 40
_MAGNETOMETER_THRESHOLD = 100

_RED_POINTS = 1
_GREEN_POINTS = 2
_BLUE_POINTS = 3
_LINEAR_FACTOR = 0.1
_LATERAL_FACTOR = 0.3
_FLIP_PENALTY = -10

state = { }

def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'IoT Lab Game Plugin',
        'version': '1.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.
    Args:
        config: JSON configuration document for the South device configuration category
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
        DataRetrievalError
    """

    time_stamp = str(datetime.datetime.now(tz=datetime.timezone.utc))
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
        accelerometer = [round(x,1) for x in motion.accelerometer()]
        if moving and state["light"] != "red" and rgb[0] > rgb[1] + _LIGHT_THRESHOLD and rgb[0] > rgb[2] + _LIGHT_THRESHOLD:
            data.append({
                    'asset': 'points/red',
                    'timestamp': time_stamp,
                    'key': str(uuid.uuid4()),
                    'readings': {
                        "points": _RED_POINTS
                    }
                })
            state["light"] = "red"
        elif moving and state["light"] != "green" and rgb[1] > rgb[0] + _LIGHT_THRESHOLD and rgb[1] > rgb[2] + _LIGHT_THRESHOLD:
            data.append({
                    'asset': 'points/green',
                    'timestamp': time_stamp,
                    'key': str(uuid.uuid4()),
                    'readings': {
                        "points": _GREEN_POINTS
                    }
                })
            state["light"] = "green"
        elif moving and state["light"] != "blue" and rgb[2] > rgb[0] + _LIGHT_THRESHOLD and rgb[2] > rgb[1] + _LIGHT_THRESHOLD:
            data.append({
                    'asset': 'points/blue',
                    'timestamp': time_stamp,
                    'key': str(uuid.uuid4()),
                    'readings': {
                        "points": _BLUE_POINTS
                    }
                })
            state["light"] = "blue"
        elif moving:
            state["light"] = "white"
        if abs(accelerometer[0]) > 0.1:
            data.append({
                    'asset': 'points/accelerometer',
                    'timestamp': time_stamp,
                    'key': str(uuid.uuid4()),
                    'readings': {
                        "points": abs(accelerometer[0] * _LINEAR_FACTOR)
                    }
                })
        if abs(accelerometer[1]) > 0.1:
            data.append({
                    'asset': 'points/lateral',
                    'timestamp': time_stamp,
                    'key': str(uuid.uuid4()),
                    'readings': {
                        "points": abs(accelerometer[1] * _LATERAL_FACTOR)
                    }
                })
        if state["inverted"] == "No" and accelerometer[2] < -0.2:
            data.append({
                    'asset': 'points/flip',
                    'timestamp': time_stamp,
                    'key': str(uuid.uuid4()),
                    'readings': {
                        "points": _FLIP_PENALTY
                    }
                })
            state["inverted"] = "Yes"
        elif accelerometer[2] > 0.2:
            state["inverted"] = "No"
    except (Exception, RuntimeError, pexpect.exceptions.TIMEOUT) as ex:
        _LOGGER.exception("IoT Lab Game exception: {}".format(str(ex)))
        raise exceptions.DataRetrievalError(ex)

    _LOGGER.debug("IoT Lab Game reading: {}".format(json.dumps(data)))
    return data


def plugin_reconfigure(handle, new_config):
    """  Reconfigures the plugin
    it should be called when the configuration of the plugin is changed during the operation of the South device service;
    The new configuration category should be passed.
    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info("Old config for Iot Lab Game plugin {} \n new config {}".format(handle, new_config))

    # Find diff between old config and new config
    diff = utils.get_diff(handle, new_config)

    # Plugin should re-initialize and restart if key configuration is changed
    if 'pollInterval' in diff:
        new_handle = copy.deepcopy(new_config)
        new_handle['restart'] = 'no'
    else:
        new_handle = copy.deepcopy(handle)
        new_handle['restart'] = 'no'
    return new_handle


def _plugin_stop(handle):
    """ Stops the plugin doing required cleanup, to be called prior to the South device service being shut down.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info('Iot Lab Game poll plugin stop.')


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the South device service being shut down.
    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _plugin_stop(handle)
    _LOGGER.info('IoT Lab Game poll plugin shut down.')
