# -*- coding: utf-8 -*-
from .errors import forbidden
from flask import g
from functools import wraps


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return func(*args, **kwargs)
        return decorated_function
    return decorator
