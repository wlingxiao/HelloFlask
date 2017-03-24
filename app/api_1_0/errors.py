# -*- coding: utf-8 -*-
from app.exceptions import ValidationError
from . import api
from flask import make_response, jsonify


def forbidden(message):
    return make_response(jsonify({'error':'forbidden', 'message':message}), 403)


def unauthorized(message):
    return make_response(jsonify({'error': 'unauthorized',
                                  'message': message}), 401)


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])

def bad_request(e):
    pass