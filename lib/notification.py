#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json


class Notification(object):

    def __init__(self, title="Mayordomo", text="", category="result", icon=None, priority=5):
        self.title = title
        self.text = text
        self.category = category
        self.icon = icon
        self.priority = priority

    def get_title(self):
        return self.title

    def get_text(self):
        return self.text

    def get_category(self):
        return self.category

    def get_icon(self):
        return self.icon

    def get_priority(self):
        return self.priority

    def set_title(self, title):
        self.title = title

    def set_text(self, text):
        self.text = text

    def set_category(self, category):
        self.category = category

    def set_icon(self, icon):
        self.icon = icon

    def set_priority(self, priority):
        self.priority = priority

    def __str__(self):
        return "Title: {}, Text: {}".format(self.title, self.text)

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    def add_notification(self, notification):
        self.title = self.title + " y " + notification.title.lower()
        self.text = self.text + " y " + notification.text.lower()
        self.priority = max(self.priority, notification.priority)
