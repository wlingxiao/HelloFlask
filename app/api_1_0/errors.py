# -*- coding: utf-8 -*-

from flask import make_response, jsonify


def forbidden(message):
    return make_response(jsonify({'error':'forbidden', 'message':message}), 403)