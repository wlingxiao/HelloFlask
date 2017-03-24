# -*- coding: utf-8 -*-
from flask import Blueprint

auth = Blueprint('auth', __name__)
import app.auth.views
