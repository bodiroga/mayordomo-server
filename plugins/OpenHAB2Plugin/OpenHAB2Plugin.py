#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import modules.openHAB2_handler as oh
from plugins.plugin_base import Plugin, register_entities, register_intents
from lib.notification import Notification


class OpenHAB2Plugin(Plugin):
    @register_intents
    def register_intents(self):
        intents = {}
        intents["set_light_state"] = {}
        intents["set_light_state"]["require"] = ["OnOffAction", "LightOnOffLabel", "LightKeyword"]

        intents["set_light_level"] = {}
        intents["set_light_level"]["require"] = ["IncreaseDecreaseAction", "LightDimLabel", "LightKeyword"]
        intents["set_light_level"]["optionally"] = ["PercentageValue"]

        intents["set_light_color"] = {}
        intents["set_light_color"]["require"] = ["LightKeyword", "LightColorLabel", "ColorKeyword", "ColorValue"]

        intents["set_shutter_level"] = {}
        intents["set_shutter_level"]["require"] = ["IncreaseDecreaseAction", "ShutterLabel", "ShutterKeyword"]
        intents["set_shutter_level"]["optionally"] = ["PercentageValue"]

        intents["get_temperature"] = {}
        intents["get_temperature"]["require"] = ["TemperatureKeyword", "TemperatureLabel"]

        intents["get_humidity"] = {}
        intents["get_humidity"]["require"] = ["HumidityKeyword", "HumidityLabel"]

        intents["get_brightness"] = {}
        intents["get_brightness"]["require"] = ["BrightnessKeyword", "BrightnessLabel"]

        intents["set_device_state"] = {}
        intents["set_device_state"]["require"] = ["OnOffAction", "SwitchableOnOffLabel"]

        return intents

    @register_entities
    def register_entities(self):

        entities = {}
        entities["LightOnOffLabel"] = {}
        entities["LightOnOffLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                                 for item in oh.get_items_by_tag("Lighting")
                                                 if item["type"] in ["Switch", "Dimmer", "Color"] or 
                                                    (item["type"] == "Group" and item["groupType"] in ["Switch", "Dimmer", "Color"])]
        entities["LightOnOffLabel"]["question"] = self._sentence("Which light?")

        entities["OnOffAction"] = {}
        entities["OnOffAction"]["values"] = [self._("switch_on", pos="verb"), self._("switch_off", pos="verb")]
        entities["OnOffAction"]["question"] = self._sentence("What do you want to do with the element?")

        entities["LightKeyword"] = {}
        entities["LightKeyword"]["values"] = [self._("light", pos="noun")]
        entities["LightKeyword"]["question"] = self._sentence("What do you want to do?")

        entities["LightDimLabel"] = {}
        entities["LightDimLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                               for item in oh.get_items_by_tag("Lighting")
                                               if item["type"] in ["Dimmer", "Color"] or
                                                (item["type"] == "Group" and item["groupType"] in ["Dimmer", "Color"])]
        entities["LightDimLabel"]["question"] = self._sentence("Which light?")

        entities["PercentageValue"] = {}
        entities["PercentageValue"]["type"] = "regex"
        entities["PercentageValue"]["values"] = "(?P<PercentageValue>\d+%)"
        entities["PercentageValue"]["question"] = self._sentence("What level?")

        entities["LightColorLabel"] = {}
        entities["LightColorLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                                 for item in oh.get_items_by_tag("Lighting")
                                                 if item["type"] in ["Color"]  or (item["type"] == "Group" and item["groupType"] == "Color")]
        entities["LightColorLabel"]["question"] = self._sentence("Which light?")

        entities["ColorKeyword"] = {}
        entities["ColorKeyword"]["values"] = [self._("color", pos='noun')]
        entities["ColorKeyword"]["question"] = self._sentence("What do you want to do with the light?")

        entities["ColorValue"] = {}
        entities["ColorValue"]["values"] = [self._("red", pos="noun"), self._("blue", pos="noun"),
                                            self._("green", pos="noun"), self._("yellow", pos="noun"),
                                            self._("white", pos="noun"), self._("purple", pos="noun")]
        entities["ColorValue"]["question"] = self._sentence("Which color?")

        entities["IncreaseDecreaseAction"] = {}
        entities["IncreaseDecreaseAction"]["values"] = [self._("increase", pos="verb"), self._("decrease", pos="verb"),
                                                        self._("dim", pos="verb")]
        entities["IncreaseDecreaseAction"]["question"] = self._sentence("What do you want to do with the light?")

        entities["ShutterLabel"] = {}
        entities["ShutterLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                                 for item in oh.get_items_by_tag("Rollershutter")
                                                 if item["type"] in ["Rollershutter"] or (item["type"] == "Group" and item["groupType"] == "Rollershutter")]
        entities["ShutterLabel"]["question"] = self._sentence("Which blinds?")

        entities["ShutterKeyword"] = {}
        entities["ShutterKeyword"]["values"] = [self._("blind", pos='noun')]
        entities["ShutterKeyword"]["question"] = self._sentence("What do you want to do?")

        entities["TemperatureKeyword"] = {}
        entities["TemperatureKeyword"]["values"] = [self._("temperature", pos="noun")]
        entities["TemperatureKeyword"]["question"] = self._sentence("What do you want to know?")

        entities["TemperatureLabel"] = {}
        entities["TemperatureLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                                  for item in oh.get_items_by_tag("CurrentTemperature")
                                                  if item["type"] in ["Number"] or (item["type"] == "Group" and item["groupType"] == "Number")]
        entities["TemperatureLabel"]["question"] = self._sentence("In which room?")

        entities["HumidityKeyword"] = {}
        entities["HumidityKeyword"]["values"] = [self._("humidity", pos="noun")]
        entities["HumidityKeyword"]["question"] = self._sentence("What do you want to know?")

        entities["HumidityLabel"] = {}
        entities["HumidityLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                               for item in oh.get_items_by_tag("CurrentHumidity")
                                               if item["type"] in ["Number"] or (item["type"] == "Group" and item["groupType"] == "Number")]
        entities["HumidityLabel"]["question"] = self._sentence("In which room?")

        entities["BrightnessKeyword"] = {}
        entities["BrightnessKeyword"]["values"] = [self._("brightness", pos="noun")]
        entities["BrightnessKeyword"]["question"] = self._sentence("What do you want to know?")

        entities["BrightnessLabel"] = {}
        entities["BrightnessLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                                 for item in oh.get_items_by_tag("CurrentBrightness")
                                                 if item["type"] in ["Number"] or (item["type"] == "Group" and item["groupType"] == "Number")]
        entities["BrightnessLabel"]["question"] = self._sentence("In which room?")

        entities["SwitchableOnOffLabel"] = {}
        entities["SwitchableOnOffLabel"]["values"] = [self._(item["label"], original_lang=self.openhab_language_alpha_3,
                                                        dynamic=(True, self))
                                                 for item in oh.get_items_by_tag("Switchable")
                                                 if item["type"] in ["Switch"] or (item["type"] == "Group" and item["groupType"] == "Switch")]
        entities["SwitchableOnOffLabel"]["question"] = self._sentence("Which device?")

        return entities

    def set_light_state(self, entities):
        original_item_label = entities["LightOnOffLabel"]["entity_original_value"]
        item_label = entities["LightOnOffLabel"]["entity_value"]
        original_new_state = entities["OnOffAction"]["entity_original_value"]

        item_name = oh.get_item_name_by_label(original_item_label, "Lighting")
        oh.send_command(item_name, self.on_off_mapping[original_new_state])
        text = self._sentence("{} light turned {}".format(item_label, self.on_off_mapping[original_new_state]))
        return Notification(text=text)

    def set_light_level(self, entities):
        original_item_label = entities["LightDimLabel"]["entity_original_value"]
        item_label = entities["LightDimLabel"]["entity_value"]
        action = entities["IncreaseDecreaseAction"]["entity_original_value"]
        item_name = oh.get_item_name_by_label(original_item_label, "Lighting")

        item_state_ = oh.get_item_state(item_name)
        item_state = float(item_state_.split(",")[1]) if "," in item_state_ else float(item_state_)
        if "PercentageValue" in entities:
            new_item_state = entities["PercentageValue"]
            if "%" in new_item_state:
                new_item_state = new_item_state.replace("%", "")
        else:
            new_item_state = item_state + 10 if action == "increase" else item_state - 10
            new_item_state = sorted((0, new_item_state, 100))[1]
        oh.send_command(item_name, new_item_state)
        text = self._sentence("{} light at {} percent".format(item_label, new_item_state))
        return Notification(text=text)

    def set_light_color(self, entities):
        original_item_label = entities["LightColorLabel"]["entity_original_value"]
        item_label = entities["LightColorLabel"]["entity_value"]
        original_new_color = entities["ColorValue"]["entity_original_value"]

        item_name = oh.get_item_name_by_label(original_item_label, "Lighting")
        oh.send_command(item_name, self.color_mapping.get(original_new_color))
        text = self._sentence("{} light {}".format(item_label, original_new_color))
        return Notification(text=text)

    def set_shutter_level(self, entities):
        original_item_label = entities["ShutterLabel"]["entity_original_value"]
        item_label = entities["ShutterLabel"]["entity_value"]
        action = entities["IncreaseDecreaseAction"]["entity_original_value"]
        item_name = oh.get_item_name_by_label(original_item_label, "RollerShutter")

        if "PercentageValue" in entities:
            new_item_state = entities["PercentageValue"]
            if "%" in new_item_state:
                new_item_state = new_item_state.replace("%", "")
        else:
            new_item_state = 0 if action == "increase" else 100
        oh.send_command(item_name, new_item_state)
        text = self._sentence("{} blinds at {} percent".format(item_label, new_item_state))
        return Notification(text=text)

    def get_temperature(self, entities):
        original_item_label = entities["TemperatureLabel"]["entity_original_value"]
        item_label = entities["TemperatureLabel"]["entity_value"]

        item_name = oh.get_item_name_by_label(original_item_label, "CurrentTemperature")
        item_state = oh.get_item_state(item_name)
        text = self._sentence("{} degrees ".format(item_state))
        return Notification(text=text)

    def get_humidity(self, entities):
        original_item_label = entities["HumidityLabel"]["entity_original_value"]
        item_label = entities["HumidityLabel"]["entity_value"]
        item_name = oh.get_item_name_by_label(original_item_label, "CurrentHumidity")
        item_state = oh.get_item_state(item_name)
        text = self._sentence("{} % ".format(item_state))
        return Notification(text=text)

    def get_brightness(self, entities):
        original_item_label = entities["BrightnessLabel"]["entity_original_value"]
        item_label = entities["BrightnessLabel"]["entity_value"]
        item_name = oh.get_item_name_by_label(original_item_label, "CurrentBrightness")
        item_state = oh.get_item_state(item_name)
        text = self._sentence("{} lux".format(item_state))
        return Notification(text=text)

    def set_device_state(self, entities):
        original_item_label = entities["SwitchableOnOffLabel"]["entity_original_value"]
        item_label = entities["SwitchableOnOffLabel"]["entity_value"]
        original_new_state = entities["OnOffAction"]["entity_original_value"]

        item_name = oh.get_item_name_by_label(original_item_label, "Switchable")
        oh.send_command(item_name, self.on_off_mapping[original_new_state])
        text = self._sentence("{} turned {}".format(item_label, self.on_off_mapping[original_new_state]))
        return Notification(text=text)

    def setup(self):
        openhab_config = self.config['openhab']
        self.openhab_language = openhab_config['language']
        self.openhab_language_alpha_3 = self.get_language_alpha_3(self.openhab_language)
        self.on_off_mapping = {"switch_on": "ON", "switch_off": "OFF"}
        self.color_mapping = {"red": "0,100,100", "blue": "240,100,100", "green": "120,100,50", "yellow": "60,100,100",
                              "white": "0,0,100", "purple": "300,100,50"}

        oh.initialize(openhab_config["host"], openhab_config["port"],
                      openhab_config["username"], openhab_config["password"])
