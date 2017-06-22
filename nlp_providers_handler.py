#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

logger = logging.getLogger("nlp_providers_handler")

LANGUAGES = {}
NLP_PROVIDERS = {}
ACTIVE_MODULE = None


def get_sentence_lemmas(sentence):
    sentence = ACTIVE_MODULE.get_sentence_lemmas(sentence)
    if sentence:
        sentence = sentence.replace("_", " ")
        sentence = sentence.replace("/100", "%")
    return sentence


def get_word_lemma(word):
    return ACTIVE_MODULE.get_word_lemma(word)


def load_nlp_providers():
    import nlp_providers
    global LANGUAGES, NLP_PROVIDERS

    NLP_PROVIDERS = nlp_providers.__all__
    for provider_name, provider_module in NLP_PROVIDERS.iteritems():
        supported_languages = provider_module.get_supported_languages()
        for language in supported_languages:
            if language not in LANGUAGES:
                LANGUAGES[language] = provider_module
            else:
                if provider_module.get_quality() > LANGUAGES[language].get_quality():
                    LANGUAGES[language] = provider_module


def stop_providers():
    for provider_name, provider_module in NLP_PROVIDERS.iteritems():
        provider_module.destroy()


def initialize(language="en"):
    global ACTIVE_MODULE
    load_nlp_providers()
    try:
        ACTIVE_MODULE = LANGUAGES[language]
    except KeyError:
        logger.error("Non of the nlp providers can handle '{}' language (default: 'en')".format(language))
        ACTIVE_MODULE = LANGUAGES["en"]
    stop_providers()
    ACTIVE_MODULE.initialize(language)
