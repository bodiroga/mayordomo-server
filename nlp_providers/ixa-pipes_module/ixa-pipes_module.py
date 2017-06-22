#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import subprocess
import os
import re
import time

logger = logging.getLogger("ixa-pipes")

IXA_FOLDER = os.path.dirname(os.path.abspath(__file__))
IXA_DEFAULT_LANG = "en"
IXA_LANG = None
IXA_POS_FOLDER = None
IXA_TOK_FOLDER = None
IXA_SERVER_PORT = 2040

QUALITY = 9
SUPPORTED_LANGUAGES = ["de", "en", "es", "eu", "fr", "gl", "it", "nl"]


def get_quality():
    return QUALITY


def get_supported_languages():
    return SUPPORTED_LANGUAGES


def initialize(language=IXA_DEFAULT_LANG, ixa_pos_folder="ixa-pipe-pos", ixa_tok_folder="ixa-pipe-tok"):
    global IXA_LANG, IXA_POS_FOLDER, IXA_TOK_FOLDER
    IXA_LANG = language
    IXA_POS_FOLDER = "{}/{}".format(IXA_FOLDER, ixa_pos_folder)
    IXA_TOK_FOLDER = "{}/{}".format(IXA_FOLDER, ixa_tok_folder)
    stop_pos_server()
    start_pos_server()
    logger.info("IXA-PIPES nlp provider started ('{}')".format(IXA_LANG))


def destroy():
    stop_pos_server()


def start_pos_server():
    model = "{0}/morph-models/{1}/{1}-pos.bin".format(IXA_POS_FOLDER, IXA_LANG)
    lemmatizermodel = "{0}/pos-models/{1}/{1}-lemma.bin".format(IXA_POS_FOLDER, IXA_LANG)
    pos_exec_file = "{}/ixa-pipe-pos-exec.jar".format(IXA_POS_FOLDER)
    command = "java -jar {} server -l {} --port {} -m {} -lm {}".format(pos_exec_file, IXA_LANG,
                                                                        IXA_SERVER_PORT, model, lemmatizermodel)
    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    time.sleep(2)
    logger.debug("POS server started on port {} (lang: '{}')".format(IXA_SERVER_PORT, IXA_LANG))


def stop_pos_server():
    pids = get_pos_server_pids()
    for pid in pids:
        command = "kill -9 {}".format(pid)
        subprocess.Popen(command.split(" "))
        logger.debug("POS server killed with pid: {}".format(pid))


def get_pos_server_pids():
    command = 'ps aux | grep "ixa-pipe-pos-exec.jar server" | grep port'
    result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
    regex = re.compile(ur"\S*\s*(\d*).*bin\n")
    matches = re.findall(regex, result)
    return matches


def get_word_lemma(word):
    return get_sentence_lemmas(word)


def get_sentence_lemmas(sentence):
    tok_exec_file = "{}/ixa-pipe-tok-exec.jar".format(IXA_TOK_FOLDER)
    pos_exec_file = "{}/ixa-pipe-pos-exec.jar".format(IXA_POS_FOLDER)
    ixa_tok_command = "java -jar {} tok -l {}".format(tok_exec_file, IXA_LANG)
    ixa_pos_command = "java -jar {} client -p {}".format(pos_exec_file, IXA_SERVER_PORT)
    command = "echo '{}' | {} | {}".format(sentence, ixa_tok_command, ixa_pos_command)
    result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
    naf = result[0]
    if not naf:
        return None
    regex = re.compile(ur"<term id=\"t\d*\" type=\"\S*\" lemma=\"(\S*)\" pos=\"\S*\" morphofeat=\"\S*\">")
    matches = re.findall(regex, naf)
    return " ".join(match.decode('utf-8') for match in matches)
