#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pyvona
import tempfile
import time
import logging
from pydub import AudioSegment

logger = logging.getLogger("IVONA")

IVONA_ACCESS_KEY = ""
IVONA_SECRET_KEY = ""
CACHE_DIRECTORY = None
QUALITY = 10

SUPPORTED_LANGUAGES = {}
VOICE_NAMES = {}

v = pyvona.create_voice(IVONA_ACCESS_KEY, IVONA_SECRET_KEY)
v.codec = 'ogg'


def get_supported_languages():
    global SUPPORTED_LANGUAGES, VOICE_NAMES
    if SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES
    try:
        voices = v.list_voices()
    except:
        return None
    voices_array = voices["Voices"]
    SUPPORTED_LANGUAGES = {}
    for voice in voices_array:
        language = voice["Language"]
        gender = voice["Gender"].lower()
        name = voice["Name"]
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
    v.voice_name = VOICE_NAMES[language][gender]
    v.region = language
    file_path = "/".join((CACHE_DIRECTORY, filename))
    try:
        with tempfile.SpooledTemporaryFile() as f:
            t = time.time()
            v.fetch_voice_fp(text, f)
            logger.debug("Time to fetch the voice file from ivona: {} seconds".format(time.time() - t))
            f.seek(0)
            t = time.time()
            ogg_audio = AudioSegment.from_ogg(f)
            logger.debug("Time to load the ogg file: {} seconds".format(time.time() - t))
        t = time.time()
        ogg_audio.export(file_path, format="wav")
        logger.debug("Time to export the ogg file to wav: {} seconds".format(time.time() - t))
    except:
        return None
    logger.info("Total time from Ivona: {} seconds".format(time.time() - start_time))
    return file_path
