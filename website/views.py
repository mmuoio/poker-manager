#from asyncio.windows_events import NULL
from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for, make_response, Response
from flask_login import login_required, current_user
from sqlalchemy import null, func, asc, desc
from .models import Player, Alias, Game, Payment, Url, Earning, PokernowId, Behavior
from . import db
import json, requests, csv
from io import StringIO

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
#@login_required
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
	return redirect(url_for('views.games'))

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

	players = Player.query.order_by(Player.name.asc()).all()
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
			r = requests.get(ledger_url, verify=False, timeout=10)
			r.raise_for_status()
		except: #(RuntimeError, TypeError, NameError):
			#print(RuntimeError,TypeError,NameError)
			flash("There was an error loading importing the game1.", category="error")
			return render_template("import_game.html", user=current_user)
		if r.status_code != 200:
			flash("There was an error loading importing the game2.", category="error")
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
	game_date = csv_dicts[0][0]['session_start_at']
	
	total_buyin = 0
	PNDictionary = []
	for each_dict in csv_dicts:
		for row in each_dict:
			total_buyin += int(row['buy_in'])
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

	from datetime import datetime, timedelta
	
	#game_date = datetime.strptime(game_date, "%Y-%m-%dT%H:%M:%SZ")
	game_date_utc = datetime(int(game_date[0:4]),int(game_date[5:7]),int(game_date[8:10]),int(game_date[11:13]),int(game_date[14:16]), 0, 0)
	delta = timedelta(hours=9)
	game_date_est = game_date_utc - delta
	
	# print("year: " + game_date[0:4])
	# print("month: " + game_date[5:7])
	# print("day: " + game_date[8:10])
	# print("hour: " + game_date[11:13])
	# print("minute: " + game_date[14:16])
	#print(game_date_utc)
	#print(game_date_est)
	#print(game_date_est.strftime('%Y-%m-%d %H:%M:%S'))
	#game_date = datetime(int(game_date[0:4]),int(game_date[5:7]),int(game_date[8:10]),int(game_date[11:13]),int(game_date[14:16]), 0, 0,timezone.est)
	game.date = game_date_est
	game.settled = True
	game.buyins = total_buyin

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

	#####################################
	#ADD POKER NOW IDS TO DB
	#####################################
	for debt in debts:
		for pn_id in debt['pn_player_id']:
			pnid_lookup = PokernowId.query.filter_by(pn_id=pn_id).first()
			if pnid_lookup:
				#DELETE EXISTING pnid
				db.session.delete(pnid_lookup)
				db.session.commit()
			#ADD TO PokernowId TABLE
			new_pnid = PokernowId(pn_id=pn_id, player_id=debt['player_id'])
			db.session.add(new_pnid)

	
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
		game = Game.query.filter_by(id=game_id).first()
		if len(game_id) < 1:
			flash('Game not found.', category='error')
	payments = Payment.query.filter_by(game_id=game_id)
	earnings = Earning.query.order_by(Earning.net.desc()).filter_by(game_id=game_id)
	players = Player.query.all()
	#print(payments)
	#print(players)

	new_earnings = []
	total_payouts = 0
	if earnings:
		for earning in earnings:
			if earning.net < 0:
				net = '-' + str("${:,}".format(abs(earning.net)))
				total_payouts += abs(earning.net)
			else:
				net = str("${:,}".format(earning.net))

			new_earnings.append({'net': earning.net, 'formatted_net' : net, 'player_id': earning.player_id})
	return render_template("payout.html", user=current_user, payments=payments, players=players, game=game, earnings=new_earnings, total_payouts=total_payouts)


@views.route('/games', methods=['GET','POST'])
def games():
	games = Game.query.order_by(Game.date.desc()).all()
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
	earnings = Earning.query.filter_by(game_id=gameID)
	behaviors = Behavior.query.filter_by(game_id=gameID)
	for url in urls:
		db.session.delete(url)
	for payment in payments:
		db.session.delete(payment)
	for earning in earnings:
		db.session.delete(earning)
	for behavior in behaviors:
		db.session.delete(behavior)
	if game:
		db.session.delete(game)
	db.session.commit()
	#games = Game.query.all()
	#return render_template("games.html", user=current_user, games=games)
	return redirect(url_for('views.games'))

	
@views.route('/profile', methods=['GET','POST'])
@login_required
def profile():
	user=current_user
	player=null
	net=0
	if user.player_id:
		player = Player.query.filter_by(id=user.player_id).first()
		#player = Player.query.filter_by(id=28).first()
		if player:
			earnings = Earning.query.filter_by(player_id=player.id)
			if earnings:
				for earning in earnings:
					#print(earning)
					net += earning.net
	return render_template("profile.html", user=current_user, player=player, net=net)
	

@views.route('/import_log', methods=['GET','POST'])
def import_log():
	#csv_file = "website\static\pn_short_log.csv"	#short log
	#csv_file = "website\static\poker_now_log_pgl7AD32cnWhunjM_Vp4O-u7a.csv"		#long log
	#csv_file = "website\static\poker_now_log_pgl1--avjXuaD_nuEtDcqij2V.csv"		
	csv_file = "website\static\poker_now_log_pglZVVjn_1wHYovvDGk7NYaaf.csv"		#name switch log
	parsedLog = parse_log(csv_file)
	game_id = request.args.get('game_id')
	
	preFlopBehavior = parsePreflopBehavior(parsedLog, game_id)
	#print(parsedLog['players'])
	return render_template("import_log.html", user=current_user)




def parse_log(csv_file):
	import re

	csv_dicts = []
	csv_file = csv.DictReader(open(csv_file))

	# Admin action regexes
	createGameRegex = '^The player "(.*) @ (.*)" created the game with a stack of (\d*(?:\.\d\d)?)'
	adminApprovedRegex = '^The admin approved the player "(.*) @ (.*)" participation with a stack of (\d*(?:\.\d\d)?)'
	seatRequestRegex = '^The player "(.*) @ (.*)" requested a seat.'
	playerJoinRegex = '^The player "(.*) @ (.*)" joined the game with a stack of (\d*(?:\.\d\d)?)'
	playerQuitRegex = '^The player "(.*) @ (.*)" quits the game with a stack of (\d*(?:\.\d\d)?)'
	sitStandRegex = '^The player "(.*) @ (.*)" (\w*)\s\w* with the stack of (\d*(?:\.\d\d)?)'

	# Hand regexes
	beginHandRegex = '^-- starting hand #(\d*).*'
	yourHandRegex = '^Your hand is (.*)'
	blindRegex = '^"(.*) @ (.*)" posts a (?:\\bmissed\\b\s|\\bmissing\\b\s)?(\\bbig\\b|\\bsmall\\b) blind of (\d*(?:\.\d\d)?)'
	straddleRegex = '^"(.*) @ (.*)" posts a straddle of (\d*(?:\.\d\d)?)'
	actionRegex = '^"(.*) @ (.*)" (\\bchecks\\b|\\bbets\\b|\\bcalls\\b|\\braises to\\b|\\bfolds\\b)(?: (\d*(?:\.\d\d)?))*'
	showRegex = '^"(.*) @ (.*)" shows a (.*)\.'
	uncalledBetRegex = '^Uncalled bet of (\d*(?:\.\d\d)?) returned to "(.*) @ (.*)"'
	collectedRegex = '^"(.*) @ (.*)" collected (\d*(?:\.\d\d)?) from pot(?: with (\w\s\\bHigh\\b|.*,?.*) \(combination\: (.*)\))?'
	cardsRegex = '^(\\b[fF]lop\\b|\\b[tT]urn\\b|\\b[rR]iver\\b)[\s\(second run\)]*: (.*)'
	rabbitHuntRegex = '^Undealt cards: (.*)'
	endHandRegex = '^-- ending hand #(\d*) --'

	# Stack regex
	stacksRegex = '^Player stacks: (.*)'
	playerStackRegex = '"(.*) @ (.*)" \((\d*(?:\.\d\d)?)\)'

	# String of cards to an array of cards
	def cardArray(cardString):
		if cardString:
			return cardString.replace('[\,\[\]]','').strip().split(' ')
		else:
			return None
	
	players = []
	hands = []
	stacks = []
	adminActions = []
	unparsedLogEntries = []
	handNumber = 0
	useCents = False
	sortedCSV = (sorted(csv_file, key = lambda i: i['order']))

	for row in sortedCSV:

		if re.search(createGameRegex, row['entry']):
			adminActions.append({
				'action': 'createGame',
				'player': re.findall(createGameRegex, row['entry'])[0][0],
				'playerId': re.findall(createGameRegex, row['entry'])[0][1],
				'amount': float(re.findall(createGameRegex, row['entry'])[0][2]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		elif re.search(adminApprovedRegex, row['entry']):
			adminActions.append({
				'action': 'adminApproved',
				'player': re.findall(adminApprovedRegex, row['entry'])[0][0],
				'playerId': re.findall(adminApprovedRegex, row['entry'])[0][1],
				'amount': float(re.findall(adminApprovedRegex, row['entry'])[0][2]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
			# Not ideal to keep setting this for each player, but it works
			if re.findall("(\d*\.\d\d)", re.findall(adminApprovedRegex, row['entry'])[0][2]):
				#if ((/(\d*\.\d\d)/).test(row['entry'].match(adminApprovedRegex)[0][2])){
				useCents = True
			
		elif re.search(seatRequestRegex, row['entry']):
			adminActions.append({
				'action': 'seatRequest',
				'player': re.findall(seatRequestRegex, row['entry'])[0][0],
				'playerId': re.findall(seatRequestRegex, row['entry'])[0][1],
				'amount': None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		elif re.search(playerJoinRegex, row['entry']):
			adminActions.append({
				'action': 'playerJoin',
				'player': re.findall(playerJoinRegex, row['entry'])[0][0],
				'playerId': re.findall(playerJoinRegex, row['entry'])[0][1],
				'amount': float(re.findall(playerJoinRegex, row['entry'])[0][2]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		elif re.search(playerQuitRegex, row['entry']):
			adminActions.append({
				'action': 'playerQuit',
				'player': re.findall(playerQuitRegex, row['entry'])[0][0],
				'playerId': re.findall(playerQuitRegex, row['entry'])[0][1],
				'amount': float(re.findall(playerQuitRegex, row['entry'])[0][2]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		elif re.search(sitStandRegex, row['entry']):
			adminActions.append({
				'action': re.findall(sitStandRegex, row['entry'])[0][2],
				'player': re.findall(sitStandRegex, row['entry'])[0][0],
				'playerId': re.findall(sitStandRegex, row['entry'])[0][1],
				'amount': float(re.findall(sitStandRegex, row['entry'])[0][3]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		# Hands
		elif re.search(beginHandRegex, row['entry']):
			handNumber += 1
			hands.append({
				'handNumber': handNumber,
				'player': None,
				'playerId': None,
				'action': 'beginHand',
				'cards': None,
				'amount': None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
			
		elif re.search(yourHandRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': None,
				'playerId': None,
				'action': 'yourHand',
				'cards': cardArray(re.findall(yourHandRegex, row['entry'])[0][0]),
				'amount': None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(straddleRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': re.findall(straddleRegex, row['entry'])[0][0],
				'playerId': re.findall(straddleRegex, row['entry'])[0][1],
				'action': 'straddle',
				'cards': None,
				'amount': float(re.findall(straddleRegex, row['entry'])[0][2]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(blindRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': re.findall(blindRegex, row['entry'])[0][0],
				'playerId': re.findall(blindRegex, row['entry'])[0][1],
				'action': re.findall(blindRegex, row['entry'])[0][2] + 'Blind',
				'cards': None,
				'amount': float(re.findall(blindRegex, row['entry'])[0][3]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(actionRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': re.findall(actionRegex, row['entry'])[0][0],
				'playerId': re.findall(actionRegex, row['entry'])[0][1],
				'action': re.findall(actionRegex, row['entry'])[0][2],
				'cards': None,
				'amount': float(re.findall(actionRegex, row['entry'])[0][3]) if re.findall(actionRegex, row['entry'])[0][3] != "" else None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(collectedRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': re.findall(collectedRegex, row['entry'])[0][0],
				'playerId': re.findall(collectedRegex, row['entry'])[0][1],
				'action': 'collected',
				'cards': cardArray(re.findall(collectedRegex, row['entry'])[0][4]) or None,
				'amount': float(re.findall(collectedRegex, row['entry'])[0][2]),
				'winningHand': re.findall(collectedRegex, row['entry'])[0][3] or None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(uncalledBetRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': re.findall(uncalledBetRegex, row['entry'])[0][1],
				'playerId': re.findall(uncalledBetRegex, row['entry'])[0][2],
				'action': 'uncalledBetReturned',
				'cards': None,
				'amount': float(re.findall(uncalledBetRegex, row['entry'])[0][0]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(showRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': re.findall(showRegex, row['entry'])[0][0],
				'playerId': re.findall(showRegex, row['entry'])[0][1],
				'action': 'show',
				'cards': cardArray(re.findall(showRegex, row['entry'])[0][2]),
				'amount': None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(rabbitHuntRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': None,
				'playerId': None,
				'action': 'rabbitHunt',
				'cards': cardArray(re.findall(rabbitHuntRegex, row['entry'])[0][0]),
				'amount': None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		elif re.search(endHandRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': None,
				'playerId': None,
				'action': 'endHand',
				'cards': None,
				'amount': None,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		# Cards dealt in the hands
		elif re.search(cardsRegex, row['entry']):
			hands.append({
				'handNumber': handNumber,
				'player': None,
				'playerId': None,
				'action': re.findall(cardsRegex, row['entry'])[0][0].lower(),
				'cards': cardArray(re.findall(cardsRegex, row['entry'])[0][1]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		# Stack sizes
		elif re.search(stacksRegex, row['entry']):
			stackSizes = []
			splitStacks = row['entry'].replace("Player stacks: ","").split(" | ")
			
			for stack in splitStacks:
				stackSizes.append({
					'player': re.findall(playerStackRegex, stack)[0][0],
					'playerId': re.findall(playerStackRegex, stack)[0][1],
					'stackSize': float(re.findall(playerStackRegex, stack)[0][2])
				})
			
			stacks.append({
				'handNumber': handNumber,
				'stackSizes': stackSizes,
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
		
		else:
			unparsedLogEntries.append(row)
	# Get list of players
	for row in hands:
		if row['player'] != None and not any(row['player'] in sublist for sublist in players) :
			pokernow_id = PokernowId.query.filter_by(pn_id=row['playerId']).first()
			if pokernow_id:
				players.append([row['player'],row['playerId'],pokernow_id.player_id])
			else:
				players.append([row['player'],row['playerId'],None])
	#for hand in stacks:
	#	print(hand)	
	#print(len(hands))
	
	return {
		'players': players,
		'numberOfHands': handNumber,
		'useCents': useCents,
		'hands': hands,
		'stacks': stacks,
		'adminActions': adminActions,
		'unparsedLogEntries': unparsedLogEntries
	}

def parsePreflopBehavior(pokerGame, game_id):
	colorsDark = ['rgba(0,129,0,1)','rgba(0,0,255,1)','rgba(255,0,0,1)','rgba(255,165,0,1)','rgba(128,0,128,1)','rgba(139,69,19,1)','rgba(0,0,0,1)', 'rgb(255,20,147,1)', 'rgba(47,79,79,1)']
	colorsLight = ['rgba(0,129,0,0.5)','rgba(0,0,255,0.5)','rgba(255,0,0,0.5)','rgba(255,165,0,0.5)','rgba(128,0,128,0.5)','rgba(139,69,19,0.5)','rgba(0,0,0,0.5)', 'rgb(255,20,147,0.5)', 'rgba(47,79,79,0.5)']
	
	hands = range(1,pokerGame['numberOfHands']+1)
	allPreflopAction = []
	for hand in hands:
		#Grab and group each action based off the hand number
		handAction = [x for x in pokerGame['hands'] if x['handNumber'] == hand]
		
		#print(handAction)
		preflopAction = []
		flopAction = []
		turnAction = []
		riverAction = []
		i = 0
		while handAction[i]['action'] != 'flop' and handAction[i]['action'] != 'collected':
			#print(handAction[i]['action'])
			preflopAction.append(handAction[i])
			i += 1
		
		street = 0
		preflopAggressor = None
		for action in handAction:
			if action['action'] in ['flop','turn','river']: street += 1
			if action['action'] == 'collected': street = 4

			if street == 0:
				#preflop stuff
				if action['action'] in ['bets', 'raises to']:
					preflopAggressor = action['playerId']
				preflopAction.append(action)
			elif street == 1:
				#flop
				flopAction.append(action)
			elif street == 2:
				#turn
				turnAction.append(action)
			elif street == 3:
				#river
				riverAction.append(action)
				print(action)

		allPreflopAction.append({'hand':hand, 'numPlayers': len(pokerGame['stacks'][hand-1]['stackSizes']), 'preflopAggressor': preflopAggressor, 'preflopAction':preflopAction, 'flopAction':flopAction, 'turnAction':turnAction, 'riverAction':riverAction})
	#print(allPreflopAction)
		

	combinedPlayerList = {}
	for player in pokerGame['players']:
		if player[2] in combinedPlayerList.keys():
			combinedPlayerList[player[2]][0].append(player[0])
			combinedPlayerList[player[2]][1].append(player[1])
		else:
			combinedPlayerList[player[2]] = [[player[0]],[player[1]]]
	

	allPlayerActions = []
	for player_id, player_values in combinedPlayerList.items():
		allPlayerActions.append({
			'player_id' : player_id,
			'names' : player_values[0],
			'pn_ids' : player_values[1],
			
			'pre_handsPlayed' : [0,0,0],
			'pre_handsRaised' : [0,0,0],
			'pre_handsParticipated' : [0,0,0],
			'3bet' : [0,0,0],
			'no_3bet' : [0,0,0],
			'4bet' : [0,0,0],
			'no_4bet' : [0,0,0],

			'post_hands_played' : [0,0,0],
			'post_hands_bet_raise' : [0,0,0],
			'post_hands_call' : [0,0,0],
			'post_hands_check' : [0,0,0],
			'cbet' : [0,0,0],
			'fold_cbet' : [0,0,0],
			'call_raise_cbet' : [0,0,0],
			'2barrel' : [0,0,0],
			'fold_2b' : [0,0,0],
			'call_raise_2b' : [0,0,0],
			'3barrel' : [0,0,0],
			'fold_3b' : [0,0,0],
			'call_raise_3b' : [0,0,0],
			'fold_3bet' : [0,0,0],
			'call_raise_3bet' : [0,0,0],
			'wtsd' : [0,0,0]
		})
	

	def findPlayerIndexByKey(key, val):
		for i, dic in enumerate(allPlayerActions):
			#print(val, dic[key])
			if isinstance(dic[key], list):
				if val in dic[key]:
					return i
			else:
				if val == dic[key]:
					return i
		return -1

	# Calculate VPIP and PFR

	def incrementCount(current, size, amount=1):
		if size <= 2:
			current[0] += amount
		elif size > 2 and size < 7:
			current[1] += amount
		else:
			current[2] += amount
		return current

	print(allPlayerActions)
	allBehavior = []
	import json
	for hand in allPreflopAction:

		print(json.dumps(hand, indent=4))
		#print(hand)
		preflopPlayed = []				# hands dealt cards
		preflopParticipated = []		# any hand not folded
		preflopRaised = []				# hands bet or raised
		preflop3bet = []				# hands 3 bet
		preflopNo3bet = []				# hands call/fold a 3 bet
		preflop4bet = []				# hands 4 bet
		preflopNo4bet = []				# hands call/fold a 4 bet

		preflopAggressor = None			# last player to bet or raise preflop
		
		postflopPlayed = []				# flops seen
		postflopRaised = []				# flops bet/raised
		postflopCalled = []				# hands called (even if bet/raised)
		postflopChecked = []			# hands checked

		cbet = []						# hands bet on the flop when PFA (interrupted by donk)
		cbetFold = []					# hands folded to a cbet
		cbetCallRaise = []				# hands called or raised to a cbet

		turnPlayed = []					# turns seen
		barrel2 = []					# hands bet on turn after cbetting (interrupted by donk)
		barrel2Fold = []				# hands folded to a double barrel
		barrel2CallRaise = []			# hands called or raised to a double barrel
		
		riverPlayed = []				# rivers seen
		barrel3 = []					# hands bet on turn after cbetting (interrupted by donk)
		barrel3Fold = []				# hands folded to a triple barrel
		barrel3CallRaise = []			# hands called or raised to a triple barrel
		
		bet3Fold = []					# hands folded to a 3 bet
		bet3CallRaise = []				# hands called or raised to a 3 bet
		wtsd = []						# hands made it to showdown

		lastAction = None
		last3Bet = False
		#preflop action
		for action in hand['preflopAction']:
			if action['player'] != None:
				preflopPlayed.append(action['player'])
			if action['action'] in ['raises to', 'bets']:
				preflopParticipated.append(action['player'])
				preflopRaised.append(action['player'])
				preflopAggressor = action['player']
			elif action['action'] in ['calls', 'straddles']:
				preflopParticipated.append(action['player'])
			
			
			#3 bet
			if lastAction == 'bets' and action['action'] == 'raises to':
				preflop3bet.append(action['player'])
				last3Bet = True
			elif lastAction == 'bets' and action['action'] != 'raises to':
				preflopNo3bet.append(action['player'])

			#4 bet
			elif lastAction == 'raises to' and action['action'] == 'raises to' and last3Bet:
				preflop4bet.append(action['player'])
			elif lastAction == 'raises to' and action['action'] != 'raises to' and last3Bet:
				preflopNo4bet.append(action['player'])
			lastAction = action['action']
		
		#flop action
		lastAction = None
		lastCBet = False
		for action in hand['flopAction']:
			if action['player'] != None:
				postflopPlayed.append(action['player'])
			if action['action'] in ['raises to', 'bets']:
				postflopRaised.append(action['player'])
			elif action['action'] in ['calls']:
				postflopCalled.append(action['player'])
			elif action['action'] in ['checks']:
				postflopChecked.append(action['player'])
			
			if action['action'] == 'bets' and action['player'] == preflopAggressor:
				cbet.append(action['player'])
				lastCBet = True
			if action['action'] == 'folds' and lastCBet:
				cbetFold.append(action['player'])
			if action['action'] in ['calls', 'raises to'] and lastCBet:
				cbetCallRaise.append(action['player'])
			lastAction = action['action']
		
		#turn action
		lastAction = None
		lastBarrel2 = False
		for action in hand['turnAction']:
			if action['player'] != None:
				turnPlayed.append(action['player'])
			# if action['action'] in ['raises to', 'bets']:
			# 	postflopRaised.append(action['player'])
			# elif action['action'] in ['calls']:
			# 	postflopCalled.append(action['player'])
			# elif action['action'] in ['checks']:
			# 	postflopChecked.append(action['player'])
			
			if action['action'] == 'bets' and action['player'] == preflopAggressor and lastCBet:
				barrel2.append(action['player'])
				lastBarrel2 = True
			if action['action'] == 'folds' and lastBarrel2:
				barrel2Fold.append(action['player'])
			if action['action'] in ['calls', 'raises to'] and lastBarrel2:
				barrel2CallRaise.append(action['player'])
			lastAction = action['action']
		
		#river action
		lastAction = None
		lastBarrel3 = False
		showdownPlayers = []
		def remove_values_from_list(the_list, val):
			return [value for value in the_list if value != val]
		for action in hand['riverAction']:
			if action['player'] != None:
				riverPlayed.append(action['player'])
				showdownPlayers.append(action['player'])
			# if action['action'] in ['raises to', 'bets']:
			# 	postflopRaised.append(action['player'])
			# elif action['action'] in ['calls']:
			# 	postflopCalled.append(action['player'])
			# elif action['action'] in ['checks']:
			# 	postflopChecked.append(action['player'])
			
			if action['action'] == 'bets' and action['player'] == preflopAggressor and lastBarrel2:
				barrel3.append(action['player'])
				lastBarrel3 = True
			if action['action'] == 'folds' and lastBarrel3:
				barrel3Fold.append(action['player'])
			if action['action'] in ['calls', 'raises to'] and lastBarrel3:
				barrel3CallRaise.append(action['player'])
			if action['action'] == 'fold':
				updatedShowdown = [value for value in showdownPlayers if value != action['player']]
				showdownPlayers = updatedShowdown
			lastAction = action['action']
		
		#showdown
		wtsd = showdownPlayers

		#run counts on each of the lists of names
		for each in [*set(preflopPlayed)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsPlayed'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsPlayed'], hand['numPlayers'])
		for each in [*set(preflopParticipated)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsParticipated'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsParticipated'], hand['numPlayers'])
		for each in [*set(preflopRaised)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsRaised'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsRaised'], hand['numPlayers'])

		for each in [*set(preflop3bet)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['3bet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['3bet'], hand['numPlayers'])
		for each in [*set(preflopNo3bet)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['no_3bet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['no_3bet'], hand['numPlayers'])
		for each in [*set(preflop4bet)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['4bet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['4bet'], hand['numPlayers'])
		for each in [*set(preflopNo4bet)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['no_4bet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['no_4bet'], hand['numPlayers'])
			
		for each in [*set(postflopPlayed)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_played'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_played'], hand['numPlayers'])
		for each in [*set(postflopRaised)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_bet_raise'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_bet_raise'], hand['numPlayers'])
		for each in [*set(postflopCalled)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_call'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_call'], hand['numPlayers'])
		for each in [*set(postflopChecked)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_check'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['post_hands_check'], hand['numPlayers'])
			
		for each in [*set(cbet)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['cbet'], hand['numPlayers'])
		for each in [*set(cbetFold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['fold_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['fold_cbet'], hand['numPlayers'])
		for each in [*set(cbetCallRaise)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_cbet'], hand['numPlayers'])
			
		for each in [*set(barrel2)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['2barrel'], hand['numPlayers'])
		for each in [*set(barrel2Fold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['fold_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['fold_2b'], hand['numPlayers'])
		for each in [*set(barrel2CallRaise)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_2b'], hand['numPlayers'])
			
		for each in [*set(barrel3)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['3barrel'], hand['numPlayers'])
		for each in [*set(barrel3Fold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['fold_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['fold_3b'], hand['numPlayers'])
		for each in [*set(barrel3CallRaise)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_3b'], hand['numPlayers'])

			
		for each in [*set(wtsd)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['wtsd'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['wtsd'], hand['numPlayers'])

	for each in allPlayerActions:
		print(each)
	return allPlayerActions

	preflopBehavior = []
	#for i, player in enumerate(pokerGame['players']):
	for player_id, player_values in combinedPlayerList.items():
		pre_handsPlayed = [0,0,0]
		pre_handsRaised = [0,0,0]
		pre_handsParticipated = [0,0,0]

		for hand in allPreflopAction:
			playerActions = [x for x in hand['preflopAction'] if x['playerId'] in player_values[1]]	#search a list of player IDs
			if (len(playerActions) >= 1):
				#pre_handsPlayed += 1
				pre_handsPlayed = incrementCount(pre_handsPlayed, hand['numPlayers'])
				allActions = []
				for action in playerActions:
					allActions.append(action['action'])
				if 'raises to' in allActions or 'bets' in allActions:
					#pre_handsRaised += 1
					#pre_handsParticipated += 1
					pre_handsRaised = incrementCount(pre_handsRaised, hand['numPlayers'])
					pre_handsParticipated = incrementCount(pre_handsParticipated, hand['numPlayers'])
				elif 'calls' in allActions or 'straddle' in allActions:
					#pre_handsParticipated += 1
					pre_handsParticipated = incrementCount(pre_handsParticipated, hand['numPlayers'])
		
		#search preflopBehavior to see if ID exists already
		playerIndex = -1
		for i, dic in enumerate(preflopBehavior):
			if dic['player_id'] == player_id:
				playerIndex = i
		if playerIndex >= 0:
			#preflopBehavior[playerIndex]['player'].append(player[0])
			preflopBehavior[playerIndex]['hu_pre_handsPlayed'] += pre_handsPlayed[0]
			preflopBehavior[playerIndex]['hu_pre_handsParticipated'] += pre_handsParticipated[0]
			preflopBehavior[playerIndex]['hu_pre_handsRaised'] += pre_handsRaised[0]
		else:
			preflopBehavior.append({
				'player': player_values[0],
				'playerId': player_values[1],
				'player_id' : player_id,
				#'borderColor': colorsDark[i],
				#'backgroundColor': colorsLight[i],
				'hu_pre_handsPlayed': pre_handsPlayed[0],
				'hu_pre_handsParticipated': pre_handsParticipated[0],
				'hu_pre_handsRaised': pre_handsRaised[0],
				
				'sr_pre_handsPlayed': pre_handsPlayed[1],
				'sr_pre_handsParticipated': pre_handsParticipated[1],
				'sr_pre_handsRaised': pre_handsRaised[1],
				
				'ft_pre_handsPlayed': pre_handsPlayed[2],
				'ft_pre_handsParticipated': pre_handsParticipated[2],
				'ft_pre_handsRaised': pre_handsRaised[2],
				#'VPIP': 0 if handsPlayed == 0 else round((handsParticipated / handsPlayed * 100),2),
				#'PFR': 0 if handsParticipated == 0 else round((handsRaised / handsParticipated * 100),2)
			})
	for eachBehavior in preflopBehavior:
		if eachBehavior['player_id']:
			behavior = db.session.query(Behavior).filter(Behavior.player_id.like(eachBehavior['player_id']),Behavior.game_id.like(game_id)).all()
			
			if not behavior:
				new_behavior = Behavior(
					game_id=game_id,
					player_id=eachBehavior['player_id'],
					hu_pre_hands_played=eachBehavior['hu_pre_handsPlayed'],
					hu_pre_hands_participated=eachBehavior['hu_pre_handsParticipated'],
					hu_pre_hands_raised=eachBehavior['hu_pre_handsRaised']
				)
				db.session.add(new_behavior)
				db.session.commit()
		#print(eachBehavior)
		
	return preflopBehavior
# 	preflopBehaviorChartData = preflopBehavior.map(function(player){
#     return {
#       label: player.player,
#       data: [{x: player.PFR, y: player.VPIP}],
#       borderWidth: 1,
#       borderColor: player.borderColor,
#       backgroundColor: player.backgroundColor
#     }
#   })
#   return {
#     type: 'scatter',
#     data: {
#       datasets: preflopBehaviorChartData
#     },
#     options: {
#       maintainAspectRatio: false,
#       elements: {
#         point: {
#           radius: 9,
#           hitRadius: 9,
#           hoverRadius: 11
#         }
#       },
#       legend: {
#         labels: {
#           usePointStyle: true,
#           pointStyle: 'circle',
#           boxWidth: 12,
#           fontSize: 16,
#           fontFamily: "Roboto, sans-serif",
#           padding: 22
#         }
#       },
#       scales: {
#         yAxes: [{
#           scaleLabel: {
#             display: true,
#             labelString: 'Voluntary Participation (% of hands called)',
#             fontSize: 18,
#             fontFamily: "Roboto, sans-serif"
#           },
#           ticks: {
#             precision:0,
#             beginAtZero: true
#           }
#         }],
#         xAxes: [{
#           scaleLabel: {
#             display: true,
#             labelString: 'Aggression (% of hands raised)',
#             fontSize: 18,
#             fontFamily: "Roboto, sans-serif"
#           },
#           ticks: {
#             precision: 0,
#             beginAtZero: true
#           }
#         }]
#       }
#     }
#   }
