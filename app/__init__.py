# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager,current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

bootstrap = Bootstrap()

app = Flask(__name__)


def create_app(config):
    # app.config['SECRET_KEY'] = config['SECRET_KEY']
    # app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['SQLALCHEMY_TRACK_MODIFICATIONS']
    app.config.from_object(config['default'])
    config['default'].init_app(app)
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # 初始化Bootstrap
    bootstrap.init_app(app)
    # 认证用户
    login_manager.init_app(app)

    # 初始化数据库
    db.init_app(app)
    db.app = app
    db.create_all()

    return app
