#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import time
import json
import devices_handler
import mqtt_handler
import engine_handler
import plugins_handler
import session_handler
import nlp_providers_handler
from lib.notification import Notification

logger = logging.getLogger("utterance_handler")

INPUT_MESSAGE_TOPIC = "mayordomo/utterance/message"


def handle_message(mosq, obj, msg):
    start_time = time.time()
    logger.debug("TOPIC: {}; MESSAGE: {}".format(msg.topic, msg.payload.decode('utf-8')))
    try:
        payload = json.loads(msg.payload)
        utterance = payload["message"]
        device_name = payload["device_name"]
        user_name = payload["user_name"]
        logger.info("New request by {} from {}: {}".format(user_name, device_name, utterance))
    except KeyError:
        logger.error("Incorrect utterance message: {}".format(msg.payload))
        return
    except ValueError:
        logger.error("Incorrect utterance message: {}".format(msg.payload))
        return

    try:
        device = devices_handler.get_device(device_name)
    except AttributeError:
        logger.error("Device '{}' is not registered, aborting message".format(device_name))
        return

    user_session = session_handler.get_user_session(user_name)
    utterance_lemmas = nlp_providers_handler.get_sentence_lemmas(utterance)
    logger.debug("Request lemma: {}".format(utterance_lemmas))

    final_intent = None
    for final_intent in engine_handler.determine_intent(utterance_lemmas, context_manager=user_session.get_context_manager()):
        pass

    logger.debug("The final intent is: {}".format(final_intent))
    if not final_intent:
        answer = Notification("Error", "Error")
        device.send_answer(answer.to_json())
        return

    for category, entity in final_intent["entities"].iteritems():
        metadata = engine_handler.get_entity_metadata(entity)
        user_session.inject_context({'data': [(entity, category, metadata)], 'key': entity, 'confidence': 0.75})

    for required_tag in final_intent["missing_required_tag"]:
        try:
            entity_category_info = engine_handler.get_entity_metadata(required_tag, True)
            text = entity_category_info.get("missing_phrase")
            answer = Notification("Pregunta", text, category="question")
        except ValueError:
            answer = Notification("Error", "Error processing the command")
        device.send_answer(answer.to_json())
        break
    else:
        for category, entity in final_intent["entities"].iteritems():
            metadata = engine_handler.get_entity_metadata(entity, True)
            if metadata:
                final_intent["entities"][category] = engine_handler.get_entity_metadata(entity, True)
            else:
                final_intent["entities"][category] = entity
        answer = plugins_handler.handle_intent(final_intent)
        if answer is None:
            answer = Notification("Error", "I don't know how to do that", category="answer")
        device.send_answer(answer.to_json())
    logger.debug("Time to process the utterance message: {} seconds".format(time.time() - start_time))


def initialize():
    session_handler.initialize()
    mqtt_handler.subscribe(INPUT_MESSAGE_TOPIC, handle_message)
    logger.debug("Subscribed to topic: {}".format(INPUT_MESSAGE_TOPIC))
