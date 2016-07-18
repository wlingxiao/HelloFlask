from flask import Flask
from app.main import blueprint


def create_app(config):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config['SECRET_KEY']
    app.register_blueprint(blueprint)
    return app
