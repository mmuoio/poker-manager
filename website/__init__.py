from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path
from flask_login import LoginManager
from sqlalchemy import MetaData
import os
from dotenv import load_dotenv
load_dotenv()

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

DB_NAME = "database.db"
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

migrate = Migrate()

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'secret_key_password_string'
	#app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
	app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL_SQ')
	
	migrate.init_app(app, db, render_as_batch=True)
	db.init_app(app)

	
	from .models import User, Player, Alias, Game, Payment, Url, Earning, PokernowId, Behavior

	#create_database(app)

	from .views import views
	from .auth import auth

	app.register_blueprint(views, url_prefix='/')
	app.register_blueprint(auth, url_prefix='/')


	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(id):
		return User.query.get(int(id))

	return app

#def create_database(app):
	#if not path.exists('website/' + DB_NAME):
	#db.create_all(app=app)
	#print('Created Database!')