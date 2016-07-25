# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_pagedown import PageDown
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

bootstrap = Bootstrap()
#
pagedown = PageDown()
app = Flask(__name__)


def create_app(config):
    app.config.from_object(config['default'])
    config['default'].init_app(app)
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    # 注册 rest_api blueprint
    from api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
    # 初始化Bootstrap
    bootstrap.init_app(app)

    # 认证用户
    login_manager.init_app(app)

    # 富文本文件
    pagedown.init_app(app)

    # 初始化数据库
    db.init_app(app)
    db.app = app
    db.create_all()

    return app
