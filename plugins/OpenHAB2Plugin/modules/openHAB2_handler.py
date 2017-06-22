#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests
import json

OPENHAB_HOST = "localhost"
OPENHAB_PORT = 8080
OPENHAB_USER = ""
OPENHAB_PASSWORD = ""


def initialize(host=OPENHAB_HOST, port=OPENHAB_PORT, user=OPENHAB_USER, password=OPENHAB_PASSWORD):
    global OPENHAB_HOST, OPENHAB_PORT, OPENHAB_USER, OPENHAB_PASSWORD
    OPENHAB_HOST = host
    OPENHAB_PORT = port
    OPENHAB_USER = user
    OPENHAB_PASSWORD = password


def send_command(item_name, command):
    url = "http://{}:{}/rest/items/{}".format(OPENHAB_HOST, OPENHAB_PORT, item_name)
    auth = (OPENHAB_USER, OPENHAB_PASSWORD)
    headers = {'content-type': "application/json; charset=utf-8"}
    r = requests.post(url, auth=auth, data=str(command))
    r.encoding = 'utf-8'
    if r.status_code != 200:
        return None
    return True


def get_item_state(item_name):
    url = "http://{}:{}/rest/items/{}".format(OPENHAB_HOST, OPENHAB_PORT, item_name)
    auth = (OPENHAB_USER, OPENHAB_PASSWORD)
    headers = {'content-type': "application/json; charset=utf-8"}
    r = requests.get(url, auth=auth, headers=headers)
    r.encoding = 'utf-8'
    if r.status_code != 200:
        return None
    info = json.loads(r.text)
    state = info["state"]
    return state


def get_all_items():
    url = "http://{}:{}/rest/items?recursive=true".format(OPENHAB_HOST, OPENHAB_PORT)
    auth = (OPENHAB_USER, OPENHAB_PASSWORD)
    headers = {'content-type': "application/json; charset=utf-8"}
    r = requests.get(url, auth=auth, headers=headers)
    r.encoding = 'utf-8'
    if r.status_code != 200:
        return None
    return json.loads(r.text)


def get_item_name_by_label(label, tag=None):
    items = get_all_items()
    if tag:
        for item in items:
            if item["label"].lower() == label.lower() and tag in item["tags"]:
                return item["name"]
    else:
        for item in items:
            if item["label"].lower() == label.lower():
                return item["name"]
    return None


def get_items_by_tag(tag):
    url = "http://{}:{}/rest/items?tags={}&recursive=true".format(OPENHAB_HOST, OPENHAB_PORT, tag)
    auth = (OPENHAB_USER, OPENHAB_PASSWORD)
    headers = {'content-type': "application/json; charset=utf-8"}
    r = requests.get(url, auth=auth, headers=headers)
    r.encoding = 'utf-8'
    if r.status_code != 200:
        return None
    return json.loads(r.text)


def get_items_by_tag_and_type(tag, item_type):
    if not tag or not item_type:
        return []
    url = "http://{}:{}/rest/items?type={}&tags={}&recursive=true".format(OPENHAB_HOST, OPENHAB_PORT, item_type, tag)
    auth = (OPENHAB_USER, OPENHAB_PASSWORD)
    headers = {'content-type': "application/json; charset=utf-8"}
    r = requests.get(url, auth=auth, headers=headers)
    r.encoding = 'utf-8'
    if r.status_code != 200:
        return None
    return json.loads(r.text)
