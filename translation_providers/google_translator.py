#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import os
import language_handler
import json
import threading
from googletrans import Translator

logger = logging.getLogger("google_translator")

CACHE_FILE_FOLDER = "/".join([os.path.dirname(os.path.abspath(__file__)), "cache"])
CACHE_FILE_NAME = "_cache"
CACHE_FILE_PATH = "/".join([CACHE_FILE_FOLDER, CACHE_FILE_NAME])

TIMER = None
CACHE = {}


def load_cache(file_path=CACHE_FILE_PATH):
    global CACHE

    try:
        with open(file_path, 'r') as fp:
            CACHE = json.load(fp)
    except IOError:
        logger.error("Cache file doesn't exist, we create a new one")
        with open(CACHE_FILE_PATH, 'w') as f:
            f.write("{}")


def save_cache(file_path=CACHE_FILE_PATH):
    global TIMER

    with open(file_path, 'w') as fp:
        json.dump(CACHE, fp)

    TIMER = None


def google_translation(sentence, src='en', dest=None, all_info=False):
    global CACHE, TIMER
    if not dest:
        dest = language_handler.get_language().get_language()

    dict_info = {"sentence": sentence, "src": src, "dest": dest}
    hash_id = str(hash(frozenset(dict_info.items())))

    if hash_id in CACHE:
        translation = CACHE[hash_id]
        return translation if not all_info else [{"value": translation, "original_value": sentence, "language": dest}]

    translator = Translator()
    translation = translator.translate(sentence, src=src, dest=dest)

    if not translation:
        return ""

    if translation.text == sentence and "_" in sentence:
        sentence_ = sentence.replace("_", " ")
        translation = translator.translate(sentence_, src=src, dest=dest)

    CACHE[hash_id] = translation.text
    if not TIMER:
        TIMER = threading.Timer(10, save_cache).start()
    if all_info:
        return [{"value": translation.text, "original_value": sentence, "language": dest}]
    return translation.text


def initialize():
    if not os.path.exists(CACHE_FILE_FOLDER):
        os.makedirs(CACHE_FILE_FOLDER)

    if not os.path.isfile(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, 'w') as f:
            f.write("{}")

    load_cache()


initialize()
