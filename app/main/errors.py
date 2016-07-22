# -*- coding: utf-8 -*-
from . import main
from flask import render_template, request, jsonify, make_response

# 状态为 404 时的返回信息
message_404 = {'error', 'not found'}


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return make_response(jsonify(message_404), 404)
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
