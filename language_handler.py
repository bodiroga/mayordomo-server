#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import json
import pycountry
import mqtt_handler
import threading
import configuration_handler

logger = logging.getLogger("language_handler")


class Language(object):

    def __init__(self, identifier):
        if "-" not in identifier:
            raise ValueError
        try:
            language_code = identifier.split("-")[0]
            if len(language_code) == 2:
                self.language = pycountry.languages.get(alpha_2=language_code).alpha_2
            elif len(language_code) == 3:
                self.language = pycountry.languages.get(alpha_3=language_code).alpha_2
            else:
                raise ValueError
        except:
            raise ValueError

        try:
            region_code = identifier.split("-")[1]
            if len(region_code) == 2:
                self.region = pycountry.countries.get(alpha_2=region_code).alpha_2
            elif len(region_code) == 3:
                self.region = pycountry.countries.get(alpha_3=region_code).alpha_3
            else:
                raise ValueError
        except:
            raise ValueError

        self.code = "{}-{}".format(self.language, self.region)

    def get_language(self):
        return self.language

    def get_language_alpha_3(self):
        return pycountry.languages.get(alpha_2=self.language).alpha_3

    def get_region(self):
        return self.region

    def get_code(self):
        return self.code

    def get_code2(self):
        return self.get_code().replace("-", "_")

    def to_json(self):
        return json.dumps({"code": self.code, "language": self.language, "region": self.region})


def get_language_alpha_3_from_alpha_2(lang):
    return pycountry.languages.get(alpha_2=lang).alpha_3


def get_language_alpha_2_from_alpha_3(lang):
    return pycountry.languages.get(alpha_3=lang).alpha_2


DEFAULT_LANGUAGE = Language("en-US")
LANGUAGE = None
LANGUAGE_TOPIC = "mayordomo/configuration/language"
LANGUAGE_SET_TOPIC = LANGUAGE_TOPIC + "/set"


def get_language():
    return LANGUAGE


def set_language(new_language):
    global LANGUAGE
    if new_language == LANGUAGE.code:
        logger.debug("Language '{}' is already in use".format(new_language))
        return
    try:
        LANGUAGE = Language(new_language)
        mqtt_handler.publish(LANGUAGE_TOPIC, LANGUAGE.to_json(), 1, True)
        logger.info("System language correctly changed to '{}'".format(LANGUAGE.code))
        configuration_handler.update_configuration("language", "language_code", LANGUAGE.code)
    except ValueError as e:
        logger.error("The language identifier '{}' is not valid: e".format(new_language, e))


def handle_message(_, __, msg):
    global LANGUAGE
    logger.debug("TOPIC: {}; MESSAGE: {}".format(msg.topic, msg.payload))
    try:
        threading.Thread(target=set_language, args=[msg.payload]).start()
    except KeyError:
        logger.error("Incorrect language set message: '{}'".format(msg.payload))


def initialize(language=None):
    global LANGUAGE
    if language is None:
        LANGUAGE = DEFAULT_LANGUAGE
    else:
        try:
            LANGUAGE = Language(language)
        except ValueError:
            LANGUAGE = DEFAULT_LANGUAGE
    mqtt_handler.subscribe(LANGUAGE_SET_TOPIC, handle_message)
    logger.debug("Subscribed to topic: {}".format(LANGUAGE_SET_TOPIC))
