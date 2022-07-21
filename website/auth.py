from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

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
			user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
			db.session.add(user)
			db.session.commit()
			flash('Account creation successful.', category='success')
			login_user(user, remember=True)
			return redirect(url_for('views.home'))

	return render_template("signup.html")