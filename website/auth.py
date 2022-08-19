from datetime import timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Player
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps

auth = Blueprint('auth', __name__)

def admin_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		#print(current_user.admin)
		if current_user.is_anonymous:
			return redirect(url_for('auth.login'))
		if current_user and current_user.admin:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('auth.login'))
	return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		data = request.form
		email = data.get('email')
		password = data.get('password')

		user = User.query.filter_by(email=email).first()
		if user:
			if check_password_hash(user.password, password):
				flash('Logged in successfully!', category='success')
				login_user(user, remember=True)
				return redirect(url_for('views.home'))
			else:
				flash('Login failed, please try again.', category='error')
		else:
			flash('Email does not exist.', category='error')
	return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
	if request.method == 'POST':
		data = request.form
		email = data.get('email')
		first_name = data.get('firstName')
		last_name = data.get('lastName')
		password1 = data.get('password1')
		password2 = data.get('password2')
		player_id = data.get('player_id')

		user = User.query.filter_by(email=email).first()
		if user:
			flash('An account with that email already exists.', category='error')
		elif len(email) < 4:
			flash('Email must be at least 4 characters long.', category='error')
		elif len(first_name) < 2:
			flash('First name must be at least 2 characters long.', category='error')
		elif len(last_name) < 2:
			flash('Last name must be at least 2 characters long.', category='error')
		elif password1 != password2:
			flash('Password does not match.', category='error')
		elif len(password1) < 4:
			flash('Password is too short.', category='error')
		else:
			#add user to db
			user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'))
			if player_id != '-1':
				user.player_id = player_id
			db.session.add(user)
			db.session.commit()
			flash('Account creation successful.', category='success')
			login_user(user, remember=True)
			return redirect(url_for('views.home'))

	players = Player.query.order_by(Player.name.asc()).all()
	return render_template("signup.html", players=players)

@auth.route('/edit_user', methods=['GET','POST'])
@login_required
def edit_user():
	user=current_user
	
	if request.method == 'POST':
		data = request.form
		email = data.get('email')
		first_name = data.get('firstName')
		last_name = data.get('lastName')
		password1 = data.get('password1')
		password2 = data.get('password2')

		if len(email) < 4:
			flash('Email must be at least 4 characters long.', category='error')
		elif len(first_name) < 2:
			flash('First name must be at least 2 characters long.', category='error')
		elif len(last_name) < 2:
			flash('Last name must be at least 2 characters long.', category='error')
		elif len(password1) > 0 and password1 != password2:
			flash('Password does not match.', category='error')
		else:
			#add user to db
			update_user = User.query.filter_by(id=current_user.id).first()
			update_user.email = email
			update_user.first_name = first_name
			update_user.last_name = last_name
			if len(password1) > 0:
				update_user.password = generate_password_hash(password1, method='sha256')
			
			db.session.commit()
			flash('User update successful.', category='success')
			return redirect(url_for('views.profile'))
		
	return render_template("edit_user.html", user=current_user)



@auth.route('/manage_users', methods=['GET','POST'])
@login_required
@admin_required
def manage_users():
	user=current_user
	users = User.query.order_by(User.first_name.asc()).all()
	
	import datetime
	today = datetime.datetime.now()
	
	return render_template("manage_users.html", user=current_user, users=users, today=today)


@auth.route('/expire_sub', methods=['POST'])
@login_required
@admin_required
def expire_sub():
	import json
	from flask import jsonify
	data = json.loads(request.data)
	userID = data['userID']
	user = User.query.get(userID)
	if user:
		user.subscribed = False
		db.session.commit()
	return jsonify({})

@auth.route('/add_30_days', methods=['POST'])
@login_required
@admin_required
def add_30_days():
	import json, datetime
	from flask import jsonify
	data = json.loads(request.data)
	userID = data['userID']
	user = User.query.get(userID)
	if user:
		new_date = user.expires_on + timedelta(days=30)
		#print(new_date)
		user.expires_on = new_date
		db.session.commit()
	return jsonify({})