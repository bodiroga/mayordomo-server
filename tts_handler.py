#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time
import os
import logging
import json
import base64
import mqtt_handler

logger = logging.getLogger("tts_handler")

TTS_TOPIC = "mayordomo/tts/get_audio"

TTS_PROVIDERS = {}
program_directory = os.path.dirname(os.path.abspath(__file__))
tts_providers_directory = "/".join((program_directory, "tts_providers"))
cache_directory = "/".join((tts_providers_directory, "cache"))


def search_file(file_name, path):
    for root, dirs, files in os.walk(path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None


def get_audio_file(text="", language="en-US", gender="female"):
    if not text:
        logger.error("Audio text cannot be empty, default message")
        text = "Error, empty audio text"
        language = "en-US"
    dict_info = {"text": text, "language": language, "gender": gender}
    logger.debug("We need to get the audio file for '{}' in '{}'".format(text, language))

    filename = str(hash(frozenset(dict_info.items()))) + '.wav'

    start_time = time.time()

    file_path = search_file(filename, cache_directory)

    if file_path:
        logger.debug("File already in cache")
    else:
        try:
            file_path = TTS_PROVIDERS[language][gender].create_audio_file(text=text, language=language, gender=gender)
        except KeyError:
            requested_language = language
            requested_gender = gender
            language = "en-US"
            gender = "female"
            file_path = TTS_PROVIDERS[language][gender].create_audio_file(text=text, language=language, gender=gender)
            logger.error("'{}' voice in '{}' can not be found, default to '{}' in '{}'".format(requested_gender,
                                                                                               requested_language,
                                                                                               gender, language))
    logger.debug("Total time to get the sound file: {} seconds".format(time.time() - start_time))
    return file_path


def message_handler(_, __, msg):
    payload = json.loads(msg.payload)
    topic = payload["topic"]
    audio_info = payload["audio_info"]
    language = "en-US" if "language" not in audio_info else audio_info["language"]
    gender = "female" if "gender" not in audio_info else audio_info["gender"]
    text = audio_info["text"]

    audio_file = get_audio_file(text, language, gender)
    with open(audio_file, 'rb') as f:
        audio_data = base64.b64encode(f.read())
    payload = {"status": 200, "data": audio_data}
    mqtt_handler.publish(topic, json.dumps(payload))


def initialization():
    global TTS_PROVIDERS
    import tts_providers
    for provider_name, provider_module in tts_providers.__all__.iteritems():
        provider_module.set_cache_directory(cache_directory)
        provider_quality = provider_module.get_quality()
        for language, gender_array in provider_module.get_supported_languages().iteritems():
            for gender in gender_array:
                try:
                    previous_provider_quality = TTS_PROVIDERS[language][gender].get_quality()
                    if provider_quality > previous_provider_quality:
                        TTS_PROVIDERS[language] = {gender: provider_module}
                except KeyError:
                    try:
                        TTS_PROVIDERS[language][gender] = provider_module
                    except KeyError:
                        TTS_PROVIDERS[language] = {gender: provider_module}


def initialize():
    mqtt_handler.subscribe(TTS_TOPIC, message_handler)
    import threading
    threading.Thread(target=initialization).start()
    logger.debug("Subscribed to topic: {}".format(TTS_TOPIC))
