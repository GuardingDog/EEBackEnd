# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from resource.controller import helloApi
from . import config


# __all__ = ['db']

app = Flask(__name__)
db = SQLAlchemy()


def create_app():
	app.config.from_object(config.Config)
	db.init_app(app)
	with app.app_context():
		# Imports
		from resource.controller import userApi, helloApi, textLibApi, dictionaryApi, eventLibApi, eventResultApi
		app.register_blueprint(helloApi.hellobp)
		app.register_blueprint(blueprint=userApi.user_api, url_prefix='/user')
		app.register_blueprint(blueprint=textLibApi.textLib_api, url_prefix='/textlibrary')
		app.register_blueprint(blueprint=dictionaryApi.dictionary_api, url_prefix='/dic')
		app.register_blueprint(blueprint=eventLibApi.eventLibApi, url_prefix='/event_lib')
		app.register_blueprint(blueprint=eventResultApi.eventResultApi, url_prefix='/event_result')
		# Create tables for our models
		db.create_all()
		return app
