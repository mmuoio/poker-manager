from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path
from flask_login import LoginManager

DB_NAME = "database.db"
db = SQLAlchemy()

def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'secret_key_password_string'
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
	#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sbhdiltjnlthsz:4f82ba903b0b4e729e03dacdabb56352b8bbbc3780ae1e28850994a6e285e9fa@ec2-3-219-229-143.compute-1.amazonaws.com:5432/d3k32m6clt9ihg'
	
	migrate = Migrate(app,db)

	db.init_app(app)

	
	from .models import User, Player, Alias, Game, Payment, Url

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