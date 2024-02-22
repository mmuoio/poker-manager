from email.policy import default
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
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
	admin = db.Column(db.Boolean, default=False)
	subscribed = db.Column(db.Boolean, default=False)
	can_upload = db.Column(db.Boolean, default=False)
	expires_on = db.Column(db.DateTime(timezone=True), default=func.now())
	

class Player(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), unique=True)
	venmo = db.Column(db.String(300))
	email = db.Column(db.String(300))
	games_played = db.Column(db.Integer, default=0)
	aliases = db.relationship('Alias', backref='player')
	earnings = db.relationship('Earning', backref='player')
	user = db.relationship('User', backref='player')
	pokernowid = db.relationship('PokernowId', backref='player')
	bankroll = db.relationship('Bankroll', backref='player')

class Alias(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	alias = db.Column(db.String(150), unique=True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

class PokernowId(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pn_id = db.Column(db.String(150), unique=True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	settled = db.Column(db.Boolean, default=False)
	date = db.Column(db.DateTime(timezone=True), default=func.now())
	urls = db.relationship('Url', backref='game')
	payments = db.relationship('Payment', backref='game')
	earnings = db.relationship('Earning', backref='game')
	buyins = db.Column(db.Integer)
	behaviors = db.relationship('Behavior', backref='game')
	decimal = db.Column(db.Boolean, default=False)

class Url(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url =  db.Column(db.String(300), unique=True)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
	imported = db.Column(db.Boolean, default=False)
	behaviors = db.relationship('Behavior', backref='url')
	game_type = db.Column(db.String(20))
	small_blind = db.Column(db.Numeric)
	big_blind = db.Column(db.Numeric)

class Payment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	amount = db.Column(db.Numeric)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
	payer = db.Column(db.Integer, db.ForeignKey('player.id'))
	payee = db.Column(db.Integer, db.ForeignKey('player.id'))

class Earning(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	net = db.Column(db.Numeric)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
	new_record = db.Column(db.Boolean, default=False)

class Behavior(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
	url_id = db.Column(db.Integer, db.ForeignKey('url.id'))
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

	hu_duration_played = db.Column(db.Integer)
	sr_duration_played = db.Column(db.Integer)
	ft_duration_played = db.Column(db.Integer)
	
	hu_pre_hands_played = db.Column(db.Integer)
	hu_pre_hands_participated = db.Column(db.Integer)
	hu_pre_hands_raised = db.Column(db.Integer)
	hu_post_hands_played = db.Column(db.Integer)
	hu_post_hands_bet_raise = db.Column(db.Integer)
	hu_post_hands_call = db.Column(db.Integer)
	hu_post_hands_check = db.Column(db.Integer)
	hu_cbet = db.Column(db.Integer)
	hu_cbet_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to cbet
	hu_cbet_fold = db.Column(db.Integer)
	hu_cbet_call_raise = db.Column(db.Integer)
	hu_turns_played = db.Column(db.Integer)
	hu_rivers_played = db.Column(db.Integer)
	hu_2barrel = db.Column(db.Integer)
	hu_2barrel_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to double barrel
	hu_3barrel = db.Column(db.Integer)
	hu_3barrel_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to triple barrel
	hu_3bet = db.Column(db.Integer)
	hu_no_3bet = db.Column(db.Integer)
	hu_4bet = db.Column(db.Integer)
	hu_no_4bet = db.Column(db.Integer)
	hu_fold_cbet = db.Column(db.Integer)
	hu_call_raise_cbet = db.Column(db.Integer)
	hu_fold_2b = db.Column(db.Integer)
	hu_call_raise_2b = db.Column(db.Integer)
	hu_fold_3b = db.Column(db.Integer)
	hu_call_raise_3b = db.Column(db.Integer)
	hu_fold_3bet = db.Column(db.Integer)
	hu_call_raise_3bet = db.Column(db.Integer)
	hu_wtsd = db.Column(db.Integer)
	
	sr_pre_hands_played = db.Column(db.Integer)
	sr_pre_hands_participated = db.Column(db.Integer)
	sr_pre_hands_raised = db.Column(db.Integer)
	sr_post_hands_played = db.Column(db.Integer)
	sr_post_hands_bet_raise = db.Column(db.Integer)
	sr_post_hands_call = db.Column(db.Integer)
	sr_post_hands_check = db.Column(db.Integer)
	sr_cbet = db.Column(db.Integer)
	sr_cbet_fold = db.Column(db.Integer)
	sr_cbet_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to cbet
	sr_cbet_call_raise = db.Column(db.Integer)
	sr_turns_played = db.Column(db.Integer)
	sr_rivers_played = db.Column(db.Integer)
	sr_2barrel = db.Column(db.Integer)
	sr_2barrel_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to double barrel
	sr_3barrel = db.Column(db.Integer)
	sr_3barrel_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to triple barrel
	sr_3bet = db.Column(db.Integer)
	sr_no_3bet = db.Column(db.Integer)
	sr_4bet = db.Column(db.Integer)
	sr_no_4bet = db.Column(db.Integer)
	sr_fold_cbet = db.Column(db.Integer)
	sr_call_raise_cbet = db.Column(db.Integer)
	sr_fold_2b = db.Column(db.Integer)
	sr_call_raise_2b = db.Column(db.Integer)
	sr_fold_3b = db.Column(db.Integer)
	sr_call_raise_3b = db.Column(db.Integer)
	sr_fold_3bet = db.Column(db.Integer)
	sr_call_raise_3bet = db.Column(db.Integer)
	sr_wtsd = db.Column(db.Integer)
	
	ft_pre_hands_played = db.Column(db.Integer)
	ft_pre_hands_participated = db.Column(db.Integer)
	ft_pre_hands_raised = db.Column(db.Integer)
	ft_post_hands_played = db.Column(db.Integer)
	ft_post_hands_bet_raise = db.Column(db.Integer)
	ft_post_hands_call = db.Column(db.Integer)
	ft_post_hands_check = db.Column(db.Integer)
	ft_cbet = db.Column(db.Integer)
	ft_cbet_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to cbet
	ft_cbet_fold = db.Column(db.Integer)
	ft_cbet_call_raise = db.Column(db.Integer)
	ft_turns_played = db.Column(db.Integer)
	ft_rivers_played = db.Column(db.Integer)
	ft_2barrel = db.Column(db.Integer)
	ft_2barrel_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to double barrel
	ft_3barrel = db.Column(db.Integer)
	ft_3barrel_check_fold = db.Column(db.Integer)	#check or fold when given the opportunity to triple barrel
	ft_3bet = db.Column(db.Integer)
	ft_no_3bet = db.Column(db.Integer)
	ft_4bet = db.Column(db.Integer)
	ft_no_4bet = db.Column(db.Integer)
	ft_fold_cbet = db.Column(db.Integer)
	ft_call_raise_cbet = db.Column(db.Integer)
	ft_fold_2b = db.Column(db.Integer)
	ft_call_raise_2b = db.Column(db.Integer)
	ft_fold_3b = db.Column(db.Integer)
	ft_call_raise_3b = db.Column(db.Integer)
	ft_fold_3bet = db.Column(db.Integer)
	ft_call_raise_3bet = db.Column(db.Integer)
	ft_wtsd = db.Column(db.Integer)
	
class Bankroll(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
	game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
	url_id = db.Column(db.Integer, db.ForeignKey('url.id'))
	url = db.relationship('Url', backref='Bankroll')
	behavior_id = db.Column(db.Integer, db.ForeignKey('behavior.id'))
	behavior = db.relationship('Behavior', backref='Bankroll')
	imported = db.Column(db.Boolean, default=False)
	date = db.Column(db.DateTime(timezone=True), default=func.now())
	location = db.Column(db.String(200), default='PokerNow')
	buyin = db.Column(db.Numeric)
	cashout = db.Column(db.Numeric)
	net = db.Column(db.Numeric)
	duration = db.Column(db.Numeric)
	hands_played = db.Column(db.Integer)