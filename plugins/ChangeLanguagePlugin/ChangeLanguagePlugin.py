#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from plugins.plugin_base import Plugin, register_intents, register_entities
from lib.notification import Notification


class ChangeLanguagePlugin(Plugin):

    @register_intents
    def register_intents(self):
        intents = {}
        intents["change_language"] = {}
        intents["change_language"]["require"] = ["SpeakKeyword", "Language"]

        return intents

    @register_entities
    def register_entities(self):
        entities = {}
        entities["SpeakKeyword"] = {}
        entities["SpeakKeyword"]["values"] = [self._("speak")]
        entities["SpeakKeyword"]["question"] = self._sentence('What do you want me to do?')

        entities["Language"] = {}
        entities["Language"]["values"] = [self._("English"), self._("Spanish"), self._("Basque"), self._("Italian"),
                                          self._("German"), self._("Galician"), self._("Catalan"), self._("French"),
                                          self._("Portuguese")]
        entities["Language"]["question"] = self._sentence("In which language?")

        return entities

    def change_language(self, entities):
        new_lang = entities["Language"]["entity_value"]
        new_original_lang = entities["Language"]["entity_original_value"]
        text = self._sentence("Switching language to {}".format(new_original_lang))
        notification = Notification(text=text)
        import threading
        topic = "mayordomo/configuration/language/set"
        threading.Timer(2, mqtt_handler.publish, [topic, self.mapping[new_original_lang]]).start()
        return notification

    def setup(self):
        global mqtt_handler
        import mqtt_handler
        self.mapping = {"English": "en-US", "Spanish": "es-ES", "Basque": "eu-ES", "Italian": "it-IT",
                        "German": "de-DE", "Galician": "gl-ES", "French": "fr-FR"}
