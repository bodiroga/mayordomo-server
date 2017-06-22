#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger("plugins_handler")

intents_dictionary = {}
plugins_dictionary = {}


def set_plugin_instance(plugin_name, plugin):
    global plugins_dictionary
    plugins_dictionary[plugin_name] = plugin


def get_plugin_instance(plugin_name):
    return plugins_dictionary[plugin_name]


def set_intent_plugin(intent_name, plugin_name):
    global intents_dictionary
    intents_dictionary[intent_name] = plugin_name


def get_intent_plugin(intent_name):
    return intents_dictionary[intent_name]


def call_plugin_method(plugin_name, method_name, args):
    plugin = get_plugin_instance(plugin_name)
    return getattr(plugin, method_name)(args)


def handle_intent(intent):
    intent_name = intent["intent_type"]
    entities = intent["entities"]
    intent_plugin_name = get_intent_plugin(intent_name)
    intent_plugin = get_plugin_instance(intent_plugin_name)
    try:
        return getattr(intent_plugin, intent_name)(entities)
    except AttributeError:
        logger.error("'{}' plugin does not implemented '{}' intent handler".format(intent_plugin_name, intent_name))
        return None


def load_plugins():
    import plugins
    reload(plugins)

    for plugin_name, plugin_module in plugins.__all__.iteritems():
        try:
            plugin_class = getattr(plugin_module, plugin_name)
        except AttributeError:
            logger.error("'{0}'s class name is not correct, it should be {0}".format(plugin_name))
            break
        plugin_instance = plugin_class()
        set_plugin_instance(plugin_instance.__class__.__name__, plugin_instance)
        try:
            plugin_instance.run()
        except AttributeError as e:
            logger.error("Plugin '{}' does not implement 'run' method ({})".format(plugin_name, e))
            import traceback
            traceback.print_exc()


def initialize():
    load_plugins()
