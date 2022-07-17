#from asyncio.windows_events import NULL
from flask import Blueprint, jsonify, render_template, request, flash, jsonify, redirect, url_for, make_response, Response
from flask_login import login_required, current_user
from sqlalchemy import null, func, asc, desc
from .models import Player, Alias, Game, Payment, Url, Earning
from . import db
import json, requests, csv
import csv
from io import StringIO
import locale
from math import floor

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
	# if request.method == 'POST':
	# 	note = request.form.get('note')

	# 	if len(note) < 1:
	# 		flash('Note is too short.', category='error')
	# 	else:
	# 		new_note = Note(data=note, user_id=current_user.id)
	# 		db.session.add(new_note)
	# 		db.session.commit()
	# 		flash('Note added!', category='success')
	return render_template("home.html", user=current_user)

#@views.route('/delete-note', methods=['POST'])
#def delete_note():
#	data = json.loads(request.data)
#	noteId = data['noteId']
#	note = Note.query.get(noteId)
#	if note:
#		if note.user_id == current_user.id:
#			db.session.delete(note)
#			db.session.commit()
#	return jsonify({})

@views.route('/players', methods=['GET','POST'])
def players():
	if request.method == 'POST':
		data = request.form
		player_name = data.get('player_name')
		player_venmo = data.get('player_venmo')
		player_alias = data.get('player_alias')

		player = Player.query.filter_by(name=player_name).first()
		alias = Alias.query.filter_by(alias=player_alias).first()

		if player:
			flash("This player already exists.", category='error')
		elif alias:
			flash("This player alias already exists.", category='error')
		elif(len(player_name) < 1):
			flash("Please enter a valid name.", category='error')
		else:
			new_player = Player(name=player_name, venmo=player_venmo)
			db.session.add(new_player)
			if player_alias:
				new_alias = Alias(alias=player_alias, player=new_player)
				db.session.add(new_alias)
			db.session.commit()
			flash('Player added', category='success')

	players = Player.query.all()
	return render_template("players.html", user=current_user, players=players)


@views.route('/edit_player', methods=['GET','POST'])
def edit_player():
	player_id = request.args.get('player_id')
	if not player_id:
		flash("That user does not exist.", category="error")
		return redirect(url_for('views.players'))
	
	player = Player.query.filter_by(id=player_id).first()
	if not player:
		flash("That player does not exist.", category="error")
		return redirect(url_for('views.players'))
	
	if request.method == 'POST':
		data = request.form
		print(data)
		if  "alias-submit" in request.form:
			print('alias submit')
			player_alias = data.get('player-alias')
			alias = Alias.query.filter_by(alias=player_alias).first()
			if len(player_alias) < 1:
				flash('Alias is too short.', category='error')
			elif alias:
				flash("This player alias already exists.", category='error')
			else:
				new_alias = Alias(alias=player_alias, player_id=player_id)
				db.session.add(new_alias)
				db.session.commit()
				flash('Alias added!', category='success')

		elif "player-submit" in request.form:
			print('player submit')
			player_name = data.get('player_name')
			player_id = data.get('player_id')
			player_venmo = data.get('player_venmo')
			if(len(player_name) < 1):
				flash("Please enter a valid name.", category='error')
			elif(len(player_id) < 1):
				flash("Invalid player.", category='error')
			else:
				update_player = Player.query.filter_by(id=player_id).first()
				update_player.name = player_name
				update_player.venmo = player_venmo
				db.session.commit()
				flash('Player added', category='success')
			

	return render_template("edit_player.html", user=current_user, player=player)

	

@views.route('/delete-alias', methods=['POST'])
def delete_alias():
	data = json.loads(request.data)
	aliasId = data['aliasId']
	alias = Alias.query.get(aliasId)
	if alias:
		db.session.delete(alias)
		db.session.commit()
	return jsonify({})


@views.route('/import_game', methods=['GET','POST'])
def import_game():
	if request.method == 'POST':
		data = request.form
		game_urls = []
		game_urls.append(data.get('game_url1'))
		if len(data.get('game_url2')) > 0:
			game_urls.append(data.get('game_url2'))
		if len(data.get('game_url3')) > 0:
			game_urls.append(data.get('game_url3'))
		new_game = False
		if len(game_urls) > 0:
			if len(game_urls[0]) == 0:
				flash("Please enter a valid URL.", category='error')
				return render_template("import_game.html", user=current_user)
			for game_url in game_urls:
				url = Url.query.filter_by(url=game_url).first()
				if url:
					flash("URL "+game_url+" has already been imported.", category="error")
					return render_template("import_game.html", user=current_user)
				else:
					if not new_game:
						new_game = Game(settled=False)
						db.session.add(new_game)
						db.session.commit()
					new_url = Url(url = game_url, game_id=new_game.id)
					db.session.add(new_url)
			db.session.commit()
			#flash('Game imported', category='success')
			return redirect(url_for('views.link_players', game_id=new_game.id))
		else:
			flash("Please enter a URL.", category="error")

	return render_template("import_game.html", user=current_user)

@views.route('/link_players', methods=['GET','POST'])
def link_players():	
	processLedger = 0
	if request.method=='POST' and request.form.get('whichForm') == 'addPlayer':
		data = request.form
		player_name = data.get('player_name')
		player_venmo = data.get('player_venmo')
		player_alias = data.get('player_alias')

		player = Player.query.filter_by(name=player_name).first()
		alias = Alias.query.filter_by(alias=player_alias).first()

		if player:
			flash("This player already exists.", category='error')
		elif alias:
			flash("This player alias already exists.", category='error')
		elif(len(player_name) < 1):
			flash("Please enter a valid name.", category='error')
		else:
			new_player = Player(name=player_name, venmo=player_venmo)
			db.session.add(new_player)
			if player_alias:
				new_alias = Alias(alias=player_alias, player=new_player)
				db.session.add(new_alias)
			db.session.commit()
			flash('Player '+player_name+' added', category='success')
	elif request.method=='POST' and request.form.get('whichForm') == 'linkPlayers':
		data = request.form
		player_link = data.getlist('player_link')
		if '-1' in player_link:
			flash("Please link every player.", category="error")
		else:
			processLedger = 1

		
	#print(request.form)
	game = Game.query.filter_by(id=request.args.get('game_id')).first()
	game_urls = game.urls
	
	#players = Player.query.all()
	#return render_template("link_players.html", user=current_user, players=players)




	if not game_urls:
		flash("Game URL is missing.", category="error")
		return redirect(url_for('views.import_game'))

	csv_dicts = []
	for game_url in game_urls:
		#####################################
		#GAME SETUP
		#####################################
		#game_url = 'https://www.pokernow.club/games/pglvS2nnCbYnGCfk17JdkB11_' #full game
		#game_url = 'https://www.pokernow.club/games/pglOLqx5yJYOEQGxL-BRzxeDp' #test game
		game_url_split = game_url.url.split('/')
		game_id = game_url_split[-1]
		ledger_url = game_url.url + '/ledger_' + game_id + '.csv'
	
	
		#####################################
		#LOAD THE GAME, ERROR IF FAILED
		#####################################
		try:
			r = requests.get(ledger_url, timeout=2)
			r.raise_for_status()
		except:
			flash("There was an error loading importing the game.", category="error")
			return render_template("import_game.html", user=current_user)
		if r.status_code != 200:
			flash("There was an error loading importing the game.", category="error")
			return render_template("import_game.html", user=current_user)
	
		#####################################
		#GAME LOADED
		#####################################

		csv_dicts.append([{k: v for k, v in row.items()} for row in csv.DictReader(r.text.splitlines(), skipinitialspace=True)])
	
	#####################################
	#GET PLAYER INDEX BY PROVIDED KEY AND VALUE
	#####################################
	def findPlayerIndexByKey(PNDictionary, key, val):
		for i, dic in enumerate(PNDictionary):
			#print(val, dic[key])
			if isinstance(dic[key], list):
				if val in dic[key]:
					return i
			else:
				if val == dic[key]:
					return i
		return -1

	#####################################
	#LOOP OVER CSV FILE AND PLACE INTO DICTIONARY
	#####################################
	PNDictionary = []
	for each_dict in csv_dicts:
		for row in each_dict:
			playerIndex = findPlayerIndexByKey(PNDictionary, 'pn_player_id', row['player_id'])
			if playerIndex >= 0:
				#player ID exists, add to it
				PNDictionary[playerIndex]['net'] += int(row['net'])
				PNDictionary[playerIndex]['balance'] += int(row['net'])
				if row['player_nickname'] not in PNDictionary[playerIndex]['player_nickname']:
					PNDictionary[playerIndex]['player_nickname'].append(row['player_nickname'])
			else:
				#add new player
				PNDictionary.append({
					'pn_player_id': [row['player_id']],
					'player_nickname': [row['player_nickname']],
					'net' : float(row['net']),
					'balance' : float(row['net']),
					'player_id' : None
					})

	#####################################
	#LOOP OVER THE DEBT DICT TO MATCH DATABASE PLAYERS OR SUBMITTED DATA
	#####################################
	for x,debt in enumerate(PNDictionary):
		if processLedger:
			debt['player_id'] = player_link[x]
		else:
			for nickname in debt['player_nickname']:
				alias = db.session.query(Alias).filter(func.lower(Alias.alias)==func.lower(nickname)).first()

				if alias:
					debt['player_id'] = alias.player_id

	#for x in PNDictionary:
	#	print(x)
	#print('break')
	
	players = Player.query.order_by(Player.name).all()
	if not processLedger:
		return render_template("link_players.html", user=current_user, players=players, ledger=PNDictionary)

	#####################################
	#COMBINE DUPLICATE PLAYER IDS
	#####################################
	finalLedger = []
	for debt in PNDictionary:
		playerIndex = findPlayerIndexByKey(finalLedger, 'player_id', debt['player_id'])
		#print(debt['player_nickname'], debt['player_id'], playerIndex)
		if playerIndex >= 0:
			for eachID in debt['pn_player_id']:
				if eachID not in finalLedger[playerIndex]['pn_player_id']:
					finalLedger[playerIndex]['pn_player_id'].append(eachID)
			
			for eachNickname in debt['player_nickname']:
				if eachNickname not in finalLedger[playerIndex]['player_nickname']:
					finalLedger[playerIndex]['player_nickname'].append(eachNickname)
			finalLedger[playerIndex]['net'] += debt['net']
			finalLedger[playerIndex]['balance'] += debt['balance']
		else:
			finalLedger.append(debt)
	#for eachDebt in finalLedger:
	#	print(eachDebt)






	#####################################
	#AFTER HERE SHOULD BE DONE ON POST
	#####################################


	
	# PNDictionary = [
	# 	{'pn_player_id': 'ID_A', 'pn_player_nickname' : 'PlayerA', 'net': 1000, 'balance': 1000},
	# 	{'pn_player_id': 'ID_B', 'pn_player_nickname' : 'PlayerB', 'net': 500, 'balance': 500},
	# 	{'pn_player_id': 'ID_C', 'pn_player_nickname' : 'PlayerC', 'net': 150, 'balance': 150},
	# 	{'pn_player_id': 'ID_D', 'pn_player_nickname' : 'PlayerD', 'net': -50, 'balance': -50},
	# 	{'pn_player_id': 'ID_E', 'pn_player_nickname' : 'PlayerE', 'net': -350, 'balance': -350},
	# 	{'pn_player_id': 'ID_F', 'pn_player_nickname' : 'PlayerF', 'net': -1250, 'balance': -1250}
	# ]

	#####################################
	#CHECKS TO SEE IF ANY PLAYER HAS A REMAINING BALANCE
	#####################################
	def balance_remaining(ledger):
		for eachRow in ledger:
			if eachRow['balance'] != 0:
				return True
		return False
	
	#####################################
	#DOES MAGIC
	#####################################
	def settle(debts):
		#Sort the ledger by balance
		debtsDict = (sorted(debts, key = lambda i: i['balance']))
		for debt in debtsDict:
			if debt['balance'] < 0:
				#if player still owes
				for i in range(len(debtsDict)):
					if debt['pn_player_id'] != debtsDict[-i]['pn_player_id']:
						#print(debt['player_nickname'][0] + ' pays ' + debtsDict[-i]['player_nickname'][0] +' ' + str(debt['balance']))
						#print(abs(debt['balance']), game.id, debt['player_id'], debtsDict[-i]['player_id'])
						new_payment = Payment(amount=abs(debt['balance']), game_id=game.id, payer=debt['player_id'], payee=debtsDict[-i]['player_id'])
						db.session.add(new_payment)
						debtsDict[-i]['balance'] = debtsDict[-i]['balance'] + debt['balance']
						debt['balance'] = 0
						debts = debtsDict
						return
	
	
	#####################################
	#LOOP OVER THE DEBT DICT UNTIL ALL BALANCED
	#####################################
	debts = (sorted(finalLedger, key = lambda i: i['net']))
	while balance_remaining(debts):
		settle(debts)
	
	for debt in debts:
		new_earning = Earning(net=debt['net'],player_id=debt['player_id'],game_id=game.id)
		db.session.add(new_earning)

	game.settled = True

	#####################################
	#ADD ANY UNUSED ALIASES
	#####################################
	for debt in debts:
		for alias in debt['player_nickname']:
			alias_lookup = Alias.query.filter_by(alias=alias).first()
			if not alias_lookup:
				#ADD TO ALIAS TABLE
				new_alias = Alias(alias=alias, player_id=debt['player_id'])
				db.session.add(new_alias)


	db.session.commit()
	
	
	#for debt in debts:
	#	print(debt)
	
	###REDIRECT TO DISPLAY PAGE


	
	#return render_template("link_players.html", user=current_user, players=players, ledger=PNDictionary)
	return redirect(url_for('views.payout', game_id=game.id))

@views.route('/payout', methods=['GET', 'POST'])
def payout():
	if request.method == 'GET':
		game_id = request.args.get('game_id')

		if len(game_id) < 1:
			flash('Game not found.', category='error')
	payments = Payment.query.filter_by(game_id=game_id)
	earnings = Earning.query.order_by(Earning.net.desc()).filter_by(game_id=game_id)
	players = Player.query.all()
	#print(payments)
	#print(players)
	locale.setlocale( locale.LC_ALL, 'English_United States.1252' )
	locale._override_localeconv = {'n_sign_posn':1}

	new_earnings = []
	for earning in earnings:
		if earning.net < 0:
			net = '-$' + str(abs(earning.net))
		else:
			net = '$' + str(earning.net)

		new_earnings.append({'net': earning.net, 'formatted_net' : net, 'player_id': earning.player_id})
	return render_template("payout.html", user=current_user, payments=payments, players=players, game_id=game_id, earnings=new_earnings)


@views.route('/games', methods=['GET','POST'])
def games():
	games = Game.query.all()
	return render_template("games.html", user=current_user, games=games)


@views.route('/export_settlement', methods=['GET','POST'])
def export_settlement():
	game_id = request.args.get('game_id')

	si = StringIO()
	cw = csv.writer(si)
	records = Payment.query.filter_by(game_id=game_id)
	
	
	# any table method that extracts an iterable will work
	cw.writerows([('From','To','Venmo','Amount')])
	for r in records:
		payer = Player.query.filter_by(id=r.payer).first()
		payee = Player.query.filter_by(id=r.payee).first()
		cw.writerows([(payer.name, payee.name, payee.venmo, r.amount)])
	response = make_response(si.getvalue())
	response.headers['Content-Disposition'] = 'attachment; filename=settlement.csv'
	response.headers["Content-type"] = "text/csv"
	response.headers["mimetype"] = "text/csv"
	return response
	


@views.route('/delete_game', methods=['GET'])
def delete_game():
	gameID = request.args.get('game_id')
	game = Game.query.filter_by(id=gameID).first()
	urls = Url.query.filter_by(game_id=gameID)
	payments = Payment.query.filter_by(game_id=gameID)
	for url in urls:
		db.session.delete(url)
	for payment in payments:
		db.session.delete(payment)
	if game:
		db.session.delete(game)
	db.session.commit()
	games = Game.query.all()
	return render_template("games.html", user=current_user, games=games)