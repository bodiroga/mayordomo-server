#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import tempfile
import time
import os
import json
import logging
import wave
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing

logger = logging.getLogger("polly")
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('nose').setLevel(logging.ERROR)

CACHE_DIRECTORY = None
QUALITY = 10

SUPPORTED_LANGUAGES = {}
VOICE_NAMES = {}


def load_credentials(credentials_path="credentials.json"):
    if not os.path.isabs(credentials_path):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        credentials_path = "/".join((dir_path, credentials_path))
    filename = credentials_path.split("/")[-1]
    try:
        with open(credentials_path, 'r') as jsonfile:
            config = json.load(jsonfile)
            os.environ["AWS_ACCESS_KEY_ID"] = config["ACCESS_KEY"]
            os.environ["AWS_SECRET_ACCESS_KEY"] = config["SECRET_KEY"]
            os.environ["AWS_DEFAULT_REGION"] = config["DEFAULT_REGION"]
            logger.debug("Configuration file '{}' loaded".format(filename))
    except IOError:
        logger.error("Configuration file '{}' does not exist".format(filename))

load_credentials()

session = Session()
polly = session.client("polly")


def get_supported_languages():
    global SUPPORTED_LANGUAGES, VOICE_NAMES
    if SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES
    try:
        voices = polly.describe_voices()
    except:
        return None
    voices_array = voices["Voices"]
    SUPPORTED_LANGUAGES = {}
    for voice in voices_array:
        language = voice["LanguageCode"]
        gender = voice["Gender"].lower()
        name = voice["Id"]
        try:
            if gender not in SUPPORTED_LANGUAGES[language]:
                SUPPORTED_LANGUAGES[language].append(gender)
        except KeyError:
            SUPPORTED_LANGUAGES[language] = [gender]
        try:
            if not VOICE_NAMES[language][gender]:
                VOICE_NAMES[language][gender] = name
        except KeyError:
            try:
                VOICE_NAMES[language][gender] = name
            except KeyError:
                VOICE_NAMES[language] = {gender: name}

    return SUPPORTED_LANGUAGES


def get_quality():
    return QUALITY


def set_cache_directory(directory):
    global CACHE_DIRECTORY
    CACHE_DIRECTORY = directory


def create_audio_file(text="", language="es-ES", gender="female"):
    start_time = time.time()
    dict_info = {"text": text, "language": language, "gender": gender}
    filename = str(hash(frozenset(dict_info.items()))) + '.wav'
    voice_id = VOICE_NAMES[language][gender]

    file_path = "/".join((CACHE_DIRECTORY, filename))

    try:
        os.makedirs(os.path.dirname(file_path))
    except OSError:
        pass
    # File doesn't exist, otherwise it will be cached
    open(file_path, 'a').close()
    
    try:
        response = polly.synthesize_speech(OutputFormat="pcm", Text=text, VoiceId=voice_id)
    except (BotoCoreError, ClientError) as error:
        logger.error("Polly service unreachable, '{}' not converted to sound: {}".format(text, error))
        return None
    
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            wavfile = wave.open(file_path, 'wb')
            wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
            wavfile.writeframes(stream.read())
            wavfile.close()
    else:
        logger.error("No audio data in polly's answer, '{}' not converted to sound".format(text))
        return None

    logger.info("Total time from polly: {} seconds".format(time.time() -  start_time))
    return(file_path)
