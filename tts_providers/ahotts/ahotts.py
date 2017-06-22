#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import time
import logging
import subprocess

logger = logging.getLogger("ahotts")

QUALITY = 9
SUPPORTED_LANGUAGES = {}

CACHE_DIRECTORY = None
AHOTTS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def get_supported_languages():
    global SUPPORTED_LANGUAGES
    if SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES
    dicts_directory = "/".join([AHOTTS_FOLDER, "bin/data_tts/dicts"])
    gender = 'female'
    for root, dirs, files in os.walk(dicts_directory):
        for file in files:
            if "_dicc.dic" in file:
                language = file.split("_")[0] + "-ES"
                SUPPORTED_LANGUAGES[language] = [gender]

    return SUPPORTED_LANGUAGES


def get_quality():
    return QUALITY


def set_cache_directory(directory):
    global CACHE_DIRECTORY
    CACHE_DIRECTORY = directory


def create_audio_file(text="", language="eu-ES", gender="female"):
    start_time = time.time()
    dict_info = {"text": text, "language": language, "gender": gender}
    filename = str(hash(frozenset(dict_info.items()))) + '.wav'
    file_path = "/".join((CACHE_DIRECTORY, filename))
    bin_folder = "/".join((AHOTTS_FOLDER, "bin"))
    data_tts_folder = "/".join((bin_folder, "data_tts"))
    bin_path = "/".join((bin_folder, "tts"))
    input_file_path = "/".join((AHOTTS_FOLDER, "input.txt"))

    with open(input_file_path, "w+") as f:
        f.write(text.encode('utf-8'))

    command = '{} -InputFile="{}" -OutputFile="{}" -Lang="{}" -DataPath="{}"'.format(bin_path, input_file_path,
                                                                                     file_path, language.split("-")[0],
                                                                                     data_tts_folder)
    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
    os.remove(input_file_path)
    logger.info("Total time from ahotts: {} seconds".format(time.time() - start_time))
    return file_path
