# -*- coding: utf-8 -*-

from flask import g, jsonify, make_response
from ..models import AnonymousUser, User
from flask_httpauth import HTTPBasicAuth
from flask_login import user_unauthorized
from errors import forbidden
from . import api
http_auth = HTTPBasicAuth()


@http_auth.verify_password
def verify_password(email, password):
    if email == '':
        g.current_user = AnonymousUser()
        return True
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user = User
    return user.verify_password(password=password)

@http_auth.error_handler
def http_auth_error():
    return user_unauthorized('Invalid credentials')

@api.route('/posts')
@http_auth.login_required
def get_post():
    pass


@api.before_app_request
@http_auth.login_required
def before_request():
    if not g.current_user.is_annymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed')


@http_auth.verify_password
def verify_password(email_or_taken, password):
    if email_or_taken == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_taken)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_taken).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password=password)


@api.route('/token')
@before_request
def get_token():
    if g.current_user.is_annymous() or g.token_used:
        return user_unauthorized('Invalid credentials')
    return jsonify({'token':g.current_user.generate_auth_token(expiration=3600), 'expiration':3600})