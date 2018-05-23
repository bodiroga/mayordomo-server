#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pyfreeling as freeling
import os
import logging

logger = logging.getLogger("freeling")

FREELING_DIR = "/usr/local"
FREELING_LANG = "es"
FREELING_DATA_DIR = FREELING_DIR + "/share/freeling"
FREELING_MODULES = {"tk": None, "sp": None, "sid": None, "mf": None, "tg": None, "parser": None}

QUALITY = 10
SUPPORTED_LANGUAGES = ["as", "ca", "cs", "cy", "de", "en", "es", "fr", "gl", "hr", "it", "nb", "pt", "ru", "sl"]


def get_quality():
    return QUALITY


def get_supported_languages():
    return SUPPORTED_LANGUAGES


def initialize(language=FREELING_LANG, freeling_dir=FREELING_DIR):
    global FREELING_DIR, FREELING_LANG, FREELING_DATA_DIR
    FREELING_DIR = freeling_dir
    FREELING_LANG = language
    FREELING_DATA_DIR = freeling_dir + "/share/freeling/"
    load_modules()
    logger.info("Freeling nlp provider started ('{}')".format(FREELING_LANG))


def destroy():
    pass


def load_modules():
    global FREELING_MODULES
    freeling.util_init_locale("default")
    op = freeling.maco_options(FREELING_LANG)
    op.set_data_files("",
                      FREELING_DATA_DIR + "common/punct.dat",
                      FREELING_DATA_DIR + FREELING_LANG + "/dicc.src",
                      FREELING_DATA_DIR + FREELING_LANG + "/afixos.dat",
                      "",
                      FREELING_DATA_DIR + FREELING_LANG + "/locucions.dat",
                      FREELING_DATA_DIR + FREELING_LANG + "/np.dat",
                      FREELING_DATA_DIR + FREELING_LANG + "/quantities.dat",
                      FREELING_DATA_DIR + FREELING_LANG + "/probabilitats.dat")
    FREELING_MODULES["tk"] = freeling.tokenizer(FREELING_DATA_DIR + FREELING_LANG + "/tokenizer.dat")
    FREELING_MODULES["sp"] = freeling.splitter(FREELING_DATA_DIR + FREELING_LANG + "/splitter.dat")
    FREELING_MODULES["sid"] = FREELING_MODULES["sp"].open_session()
    FREELING_MODULES["mf"] = freeling.maco(op)
    FREELING_MODULES["mf"].set_active_options(False, True, True, True,
                               True, True, False, True,
                               True, True, True, True)
    FREELING_MODULES["tg"] = freeling.hmm_tagger(FREELING_DATA_DIR + FREELING_LANG + "/tagger.dat", True, 2)

    if os.path.isdir(FREELING_DATA_DIR + FREELING_LANG + "/chucker/grammar-chunk.dat"):
        FREELING_MODULES["parser"] = freeling.chart_parser(FREELING_DATA_DIR + FREELING_LANG
                                                           + "/chunker/grammar-chunk.dat")


def get_word_info(word):
    word = word.split("_")[0]
    l = FREELING_MODULES["tk"].tokenize(word)
    ls = FREELING_MODULES["sp"].split(l)
    ls = FREELING_MODULES["mf"].analyze(ls)
    ls = FREELING_MODULES["tg"].analyze(ls)
    w = ls[0].get_words()[0]
    a = w.get_analysis()[0]
    result = dict(input=word,
                  word=w.get_form(),
                  lemma=a.get_lemma(),
                  tag=a.get_tag(),
                  prob=a.get_prob())
    if a.get_prob() > 0.50:
        return result
    return None


def get_word_lemma(word):
    info = get_word_info(word)
    if info:
        return info["lemma"]
    return None


def get_sentence_lemmas(sentence):
    new_sentence = []
    l = FREELING_MODULES["tk"].tokenize(sentence)
    ls = FREELING_MODULES["sp"].split(l)
    ls = FREELING_MODULES["mf"].analyze(ls)
    ls = FREELING_MODULES["tg"].analyze(ls)
    if FREELING_MODULES["parser"]:
        ls = FREELING_MODULES["parser"].analyze(ls)
    for item in ls:
        words = item.get_words()
        for word in words:
            new_sentence.append(word.get_lemma())
    return " ".join(new_sentence)


def get_sentence_lemmas2(sentence):
    new_sentence = ""
    for word in sentence.split(" "):
        new_sentence += " {}".format(get_word_lemma(word))
    return new_sentence
