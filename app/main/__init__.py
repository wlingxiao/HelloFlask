# -*- coding: utf-8 -*-
from flask import Blueprint

main = Blueprint('Blueprint', __name__)
import views, errors
