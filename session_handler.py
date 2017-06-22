#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import threading
from adapt.context import ContextManager

logger = logging.getLogger("session_handler")

session_timeout = 300
sessions = {}


class Session(object):

    def __init__(self, username):
        self.username = username
        self.context_manager = ContextManager()
        self.context_timer = threading.Timer(session_timeout, self.restart_context_manager)
        self.context_timer.start()

    def get_context_manager(self):
        self.restart_timer()
        return self.context_manager

    def inject_context(self, entity, metadata={}):
        self.context_manager.inject_context(entity, metadata)

    def restart_timer(self):
        logger.debug("Context timer restarted for user {}".format(self.username))
        self.context_timer.cancel()
        self.context_timer = threading.Timer(session_timeout, self.restart_context_manager)
        self.context_timer.start()

    def restart_context_manager(self):
        logger.debug("Context for user {} restarted after {} seconds".format(self.username, session_timeout))
        self.context_manager = ContextManager()


def get_user_session(username):
    try:
        return sessions[username]
    except KeyError:
        logger.debug("No active session for user: {}".format(username))
        new_session = Session(username)
        sessions[username] = new_session
        return new_session


def initialize():
    global sessions
    sessions = {}
