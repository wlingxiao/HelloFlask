# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))
# Config = {
#     'SECRET_KEY':'some string',
#     # 'SQLALCHEMY_DATABASE_URI':'mysql://root:123456@localhost/hello_flask',
#     'SQLALCHEMY_DATABASE_URI':'sqlite:///' + os.path.join(basedir, 'data.db'),
#     'SQLALCHEMY_COMMIT_ON_TEARDOWN':True,
#     'SQLALCHEMY_TRACK_MODIFICATIONS':True
# }
class Config:
    SECRET_KEY='some string'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db'),
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    'default':DevelopmentConfig,
    'development':DevelopmentConfig
}