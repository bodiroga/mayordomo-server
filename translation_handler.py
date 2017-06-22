#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import language_handler
import os
import gettext
import sys
from translation_providers import google_translator
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError

logger = logging.getLogger("translation_handler")


TRANSLATION_FILES = {}


def modified_ugettext(self, message):
    missing = object()
    tmsg = self._catalog.get(message, missing)
    if tmsg is missing:
        if self._fallback:
            return self._fallback.ugettext(message)
        return ""
    return tmsg

gettext.GNUTranslations.ugettext = modified_ugettext


class TranslationFile(object):

    def __init__(self, module):
        global TRANSLATION_FILES
        self.plugin_path = sys.modules[module.__class__.__module__].__file__.replace(".pyc", ".py")
        self.plugin_folder = os.path.dirname(self.plugin_path)
        self.plugin_name = self.plugin_path.split("/")[-1]
        self.po_folder = "/".join([self.plugin_folder, "locale", language_handler.get_language().get_code2(),
                                   "LC_MESSAGES"])
        self.po_name = self.plugin_name.replace(".py", ".po")
        self.po_path = "/".join([self.po_folder, self.po_name])
        self.mo_path = self.po_path.replace(".po", ".mo")
        self.po = None
        self.create_translation_file()
        TRANSLATION_FILES[self.plugin_name] = self

    def extract_translations_from_code(self):
        import re
        lemma_regex = re.compile(ur"self\._\(\"([^\"]*)\"")
        sentence_regex = re.compile(ur"self\._sentence\(\"([^\"]*)\"")

        with open(self.plugin_path) as f:
            matches = []
            for i, line in enumerate(f):
                lemma_matches = re.findall(lemma_regex, line)
                sentence_matches = re.findall(sentence_regex, line)
                for lemma in lemma_matches:
                    matches.append([i, lemma])
                for sentence in sentence_matches:
                    matches.append([i, sentence])

        return matches

    def create_translation_file(self):
        import polib
        matches = self.extract_translations_from_code()

        exist = True

        if not os.path.exists(self.po_folder):
            os.makedirs(self.po_folder)

        if not os.path.isfile(self.po_path):
            exist = False
            with open(self.po_path, 'w'):
                pass

        self.po = polib.pofile(self.po_path)

        if not exist:
            logger.debug("Creating '{}' file because it doesn't exist".format(self.po_name))
            for line, identifier in matches:
                entry = polib.POEntry(msgid=identifier, msgstr='')
                entry.occurrences = [(self.plugin_name, line)]
                self.po.append(entry)
            self.po.save()

        self.po.save_as_mofile(self.mo_path)

    def add_new_entry(self, identifier, msgstr='', line=0):
        import polib
        entry = polib.POEntry(msgid=identifier, msgstr=msgstr)
        entry.occurrences = [(self.plugin_name, line)]

        if entry not in self.po:
            self.po.append(entry)
            self.po.save()
            self.po.save_as_mofile(self.mo_path)


def wordnet_translation(word, pos=None, original_lang='eng', translation_lang=None, dynamic=(False, None)):
    if not translation_lang:
        translation_lang = language_handler.get_language().get_language_alpha_3()

    if pos:
        try:
            mapping = {"noun": wn.NOUN, "verb": wn.VERB, "adj": wn.ADJ, "adv": wn.ADV}
            pos = mapping.get(pos.lower())
        except KeyError:
            pos = None

    final_lemmas = []

    try:
        for synsets in wn.synsets(word, pos=pos, lang=original_lang):
            for lemma in synsets.lemmas(translation_lang):
                lemma_name = lemma.name().replace("_", " ")
                for saved_lemmas in final_lemmas:
                    if lemma_name in saved_lemmas.values():
                        break
                info = {"value": lemma_name, "original_value": word,
                        "language": language_handler.get_language().get_code()}
                final_lemmas.append(info)
    except WordNetError:
        logger.error("Language {} not supported by WordNet".format(translation_lang))

    if not final_lemmas:
        if original_lang == translation_lang:
            return word
        else:
            original_lang = language_handler.get_language_alpha_2_from_alpha_3(original_lang)
            translation_lang = language_handler.get_language_alpha_2_from_alpha_3(translation_lang)
            return google_translator.google_translation(word, src=original_lang, dest=translation_lang, all_info=True)

    return final_lemmas


def multilingual(self):

    lang_trans = language_handler.get_language()

    path = sys.modules[self.__class__.__module__].__file__
    localedir = os.path.join(os.path.abspath(os.path.dirname(path)), 'locale')

    try:
        translate = gettext.translation(self.__class__.__name__, localedir,
                                        languages=[lang_trans.get_code2()])

        def _modified(word, pos=None, original_lang='eng', translation_lang=None, dynamic=(False, None)):
            if not translation_lang:
                translation_lang = language_handler.get_language().get_language_alpha_3()

            translation = translate.ugettext(word)
            if not translation:
                if dynamic[0]:
                    plugin_path = sys.modules[dynamic[1].__class__.__module__].__file__.replace(".pyc", ".py")
                    plugin_name = plugin_path.split("/")[-1]
                    TRANSLATION_FILES[plugin_name].add_new_entry(word)
                return wordnet_translation(word, pos, original_lang=original_lang, translation_lang=translation_lang)
            if word == translation:
                logger.warn("Strange translation for '{}' in '{}', trying with wordnet".format(word, translation_lang))
                return wordnet_translation(word, pos, original_lang=original_lang, translation_lang=translation_lang)

            return [{"value": translation, "original_value": word,
                     "language": language_handler.get_language().get_code()}]

        _ = _modified
        _sentence = google_translator.google_translation
    except IOError:
        _ = wordnet_translation
        _sentence = google_translator.google_translation

    return _, _sentence
