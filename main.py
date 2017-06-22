#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import signal
import time
import logging
import mqtt_handler
import engine_handler
import utterance_handler
import devices_handler
import tts_handler
import plugins_handler
import language_handler
import configuration_handler as config
import nlp_providers_handler

logging.basicConfig(format='%(asctime)s %(levelname)-8s - %(name)-25s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger("main")


def signal_handler(signal, frame):
    mqtt_handler.stop()
    nlp_providers_handler.stop_providers()
    logger.info("Main program stopped")


def load_modules():
    start_time = time.time()
    logger.info("Starting main program")
    config.load_configuration()
    engine_handler.initialize_engine()
    mqtt_handler.initialize(config.get_section("mqtt")["host"], config.get_section("mqtt")["port"],
                            config.get_section("mqtt")["username"], config.get_section("mqtt")["password"])
    language_handler.initialize(config.get_section("language")["language_code"])
    nlp_providers_handler.initialize(language_handler.get_language().language)
    utterance_handler.initialize()
    tts_handler.initialize()
    devices_handler.initialize()
    plugins_handler.initialize()
    mqtt_handler.start()
    logger.info("Main program started in {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    load_modules()

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
