#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import plugins_handler
import language_handler
import logging
import json
import engine_handler
import translation_handler
from adapt.intent import IntentBuilder

logger = logging.getLogger("plugin_base")


def register_entities(func):
    def wrapper(self):
        for category, info in func(self).iteritems():
            if "question" in info:
                question = info["question"]
            else:
                logger.warn("'{}' entity does not have a question (default)".format(category))
                question = "{} missing information".format(category)
            entities = []
            if "values" in info:
                entities = info["values"]
            else:
                logger.warn("'{}' entity does not have any value".format(category))
            if "type" in info and info["type"] == "regex":
                logger.debug("Adding '{}' regex entity to {} category".format(entities, category))
                engine_handler.get_engine().register_regex_entity(entities)
                continue
            for entity in entities:
                if type(entity) in (str, unicode):
                    logger.debug("Adding {} entity to {} category".format(entity, category))
                    metadata = json.dumps({"entity_value": entity, "entity_type": category, "missing_phrase": question,
                                           "language": language_handler.get_language().get_code(),
                                           "entity_original_value": entity})
                    engine_handler.get_engine().register_entity(entity, category, metadata=metadata)
                elif type(entity) == list:
                    for e in entity:
                        logger.debug("Adding {} entity to {} category".format(e["value"], category))
                        metadata = json.dumps({"entity_value": e["value"], "entity_type": category,
                                               "missing_phrase": question, "language": e["language"],
                                               "entity_original_value": e["original_value"]})
                        engine_handler.get_engine().register_entity(e["value"], category, metadata=metadata)
        return func(self)
    return wrapper


def register_intents(func):
    def wrapper(self):
        for intent_name, info in func(self).iteritems():
            intent = IntentBuilder(intent_name)

            if "require" not in info:
                info["require"] = []
            if "optionally" not in info:
                info["optionally"] = []
            if "one of" not in info:
                info["one of"] = []

            for require in info["require"]:
                intent.require(require)
            for optionally in info["optionally"]:
                intent.optionally(optionally)
            for one_of in info["one of"]:
                intent.one_of(one_of)
            intent = intent.build()

            logger.debug("Adding {} intent through {} plugin".format(intent_name, self.__class__.__name__))
            engine_handler.get_engine().register_intent_parser(intent)
            plugins_handler.set_intent_plugin(intent_name, self.__class__.__name__)
        return func(self)
    return wrapper


class Plugin(object):

    def get_language_alpha_2(self, lang):
        try:
            return language_handler.Language(lang).get_code()
        except ValueError:
            return None

    def get_language_alpha_3(self, lang):
        try:
            return language_handler.Language(lang).get_language_alpha_3()
        except ValueError:
            return None

    def load_configuration(self):
        import os
        import sys
        import yaml
        plugin_path = sys.modules[self.__class__.__module__].__file__

        configuration_path = "/".join([os.path.dirname(plugin_path), 'configuration.yml'])

        try:
            with open(configuration_path, 'r') as ymlfile:
                self.config = yaml.load(ymlfile)
        except IOError:
            self.config = {}

    def register_intents(self):
        return {}

    def register_entities(self):
        return {}

    def setup(self):
        pass

    def run(self):
        translation_handler.TranslationFile(self).create_translation_file()
        self._, self._sentence = translation_handler.multilingual(self)
        self.load_configuration()
        self.setup()
        self.register_entities()
        self.register_intents()
