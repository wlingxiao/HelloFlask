# -*- coding: utf-8 -*-
from flask import Blueprint
from app.models import Permission
main = Blueprint('main', __name__)


@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)

from . import views, errors
