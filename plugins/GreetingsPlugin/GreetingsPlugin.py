#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from plugins.plugin_base import Plugin, register_entities, register_intents
from lib.notification import Notification


class GreetingsPlugin(Plugin):

    @register_intents
    def register_intents(self):
        intents = {}
        intents["greet_person"] = {}
        intents["greet_person"]["require"] = ["GreetingsAction", "Person"]

        return intents

    @register_entities
    def register_entities(self):
        entities = {}
        entities["Person"] = {}
        entities["Person"]["values"] = ["Ana", "Ane", "Aitor", "Iker", "Iñaki", "Jon", "Jokin", "Kepa", "Maite",
                                        "Markel", "Mikel", "Miren", "Nerea", "Rodri", "Tamara", "Mike", "Ellen",
                                        "Emily", "Jessica", "Jack", "Harry", "Charlie"]
        entities["Person"]["question"] = self._sentence("To whom do you want me to say hello?")

        entities["GreetingsAction"] = {}
        entities["GreetingsAction"]["values"] = [self._("hi"), self._("hello"), self._("greet"),
                                                 self._("introducie")]
        entities["GreetingsAction"]["question"] = self._sentence('What should I say?')

        return entities

    def greet_person(self, entities):
        person_name = entities["Person"]["entity_value"]
        text = self._sentence("Hello {}, how are you?".format(person_name))
        notification = Notification(text=text)
        return notification
