#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import mqtt_handler

logger = logging.getLogger("devices_handler")

REGISTER_TOPIC = "mayordomo/devices/register/+"

devices = {}


class Device(object):

    def __init__(self, name=None, description="", owner="unknown", location="unknown"):
        if not name:
            raise ValueError
        self.name = name
        self.description = description
        self.owner = owner
        self.location = location
        self.online = 0
        self.device_topic = "mayordomo/devices/{}".format(self.name)
        self.answer_topic = "{}/answer".format(self.device_topic)
        self.online_topic = "{}/$online".format(self.device_topic)
        mqtt_handler.subscribe(self.online_topic, self.online_handler)

    def get_name(self):
        return self.name

    def online_handler(self, _, __, msg):
        try:
            online = int(msg.payload)
        except ValueError:
            logger.error("Online status of '{}' can not be decoded correctly ('{}')".format(self.name, msg.payload))
            return
        if online in [0, 1]:
            self.online = online

    def is_online(self):
        return True if self.online else False

    def send_answer(self, answer):
        mqtt_handler.publish(self.answer_topic, answer)

    def __str__(self):
        return "'{}' ('{}' in {} location)".format(self.name, self.description, self.location)


def get_device(name):
    if name in devices:
        return devices[name]
    return None


def handle_message(_, __, msg):
    logger.debug("TOPIC: {}; MESSAGE: {}".format(msg.topic, msg.payload))
    device_info = json.loads(msg.payload)
    try:
        device_name = device_info["name"]
        if not get_device(device_name):
            new_device = Device(device_name, device_info["description"], device_info["owner"], device_info["location"])
            devices[new_device.get_name()] = new_device
            logger.info("New device added to the database: {}".format(new_device))
        else:
            logger.warn("Device '{}' already in the database".format(device_name))
    except KeyError:
        logger.error("Incorrect device register message: {}".format(msg.payload))


def initialize():
    mqtt_handler.subscribe(REGISTER_TOPIC, handle_message)
    logger.debug("Subscribed to topic: {}".format(REGISTER_TOPIC))
