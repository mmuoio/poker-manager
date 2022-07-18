from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(150), unique=True)
	password = db.Column(db.String(150))
	first_name = db.Column(db.String(150))
	last_name = db.Column(db.String(150))

class Player(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), unique=True)
	venmo = db.Column(db.String(300))
	email = db.Column(db.String(300))
	games_played = db.Column(db.Integer, default=0)
	aliases = db.relationship('Alias', backref='player')
	earnings = db.relationship('Earning', backref='player')

class Alias(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	alias = db.Column(db.String(150), unique=True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	settled = db.Column(db.Boolean)
	date = db.Column(db.DateTime(timezone=True), default=func.now())
	urls = db.relationship('Url', backref='game')
	payments = db.relationship('Payment', backref='game')
	earnings = db.relationship('Earning', backref='game')

class Url(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url =  db.Column(db.String(300), unique=True)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

class Payment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	amount = db.Column(db.Integer)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
	payer = db.Column(db.Integer, db.ForeignKey('player.id'))
	payee = db.Column(db.Integer, db.ForeignKey('player.id'))

class Earning(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	net = db.Column(db.Integer)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))