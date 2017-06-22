#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import json
from adapt.engine import IntentDeterminationEngine

logger = logging.getLogger("engine_handler")

engine = None


def initialize_engine():
    global engine
    engine = IntentDeterminationEngine()
    logger.debug("Engine initialized")


def get_engine():
    return engine


def is_engine_initialized():
    return engine is not None


def determine_intent(utterance, num_results=1, include_tags=False, context_manager=None):
    for intent in engine.determine_intent(utterance, num_results=num_results,
                                          include_tags=include_tags, context_manager=context_manager):
        yield intent


def search_entity(entity):
    for r in engine.trie.lookup(entity.lower()):
        return r
    logger.error("Entity '{}' can not be found".format(entity))


def get_entity_metadata(entity, dict=False):
    found_entity_data = search_entity(entity)
    if not found_entity_data:
        return None
    for info in next(iter(found_entity_data.get("data"))):
        if info[0] == '{':
            if dict:
                return json.loads(info)
            return info
