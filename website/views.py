#from asyncio.windows_events import NULL
from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for, make_response, Response
from flask_login import login_required, current_user, AnonymousUserMixin
from sqlalchemy import null, func, asc, desc
from .models import Bankroll, Player, Alias, Game, Payment, Url, Earning, PokernowId, Behavior
from . import db
import json, requests, csv
from io import StringIO
from functools import wraps

import boto3


s3 = boto3.client('s3',
                    aws_access_key_id='AKIAYX7T7SKTAWVRLH56',
                    aws_secret_access_key= '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',
                    #aws_session_token='secret token here'
					region_name='us-east-1'
                     )
BUCKET_NAME='pokermanager'


def isfile_s3(key: str) -> bool:
	#return True
	s3_resource = boto3.resource('s3')
	bucket = s3_resource.Bucket(BUCKET_NAME)
	"""Returns T/F whether the file exists."""
	objs = list(bucket.objects.filter(Prefix=key))
	return len(objs) == 1 and objs[0].key == key

	#s3 = boto3.client('s3')
	#try:
	#	s3.head_object(Bucket=BUCKET_NAME, Key=key)
	#	return True
	#except ClientError:
	#	return False

views = Blueprint('views', __name__)

@views.route('/files', methods=['GET', 'POST'])
def files():
	s3_resource = boto3.resource('s3')
	my_bucket = s3_resource.Bucket(BUCKET_NAME)
	summaries = my_bucket.objects.all()
	return render_template('files.html', my_bucket=my_bucket, files=summaries)


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

def sub_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		#print(current_user.admin)
		if current_user.is_anonymous:
			return redirect(url_for('auth.login'))
		if current_user and current_user.subscribed:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('auth.login'))
	return decorated_function

def can_upload(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		#print(current_user.admin)
		if current_user.is_anonymous:
			return redirect(url_for('auth.login'))
		if current_user and current_user.can_upload:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('auth.login'))
	return decorated_function

@views.route('/home', methods=['GET', 'POST'])
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
	return render_template("home.html")



@views.route('/', methods=['GET', 'POST'])
#@login_required
def index():
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
@admin_required
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
@admin_required
def delete_alias():
	data = json.loads(request.data)
	aliasId = data['aliasId']
	alias = Alias.query.get(aliasId)
	if alias:
		db.session.delete(alias)
		db.session.commit()
	return jsonify({})


@views.route('/import_game', methods=['GET','POST'])
@can_upload
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
						db.session.flush()
					new_url = Url(url = game_url, game_id=new_game.id)
					db.session.add(new_url)
			db.session.commit()
			#flash('Game imported', category='success')
			return redirect(url_for('views.link_players', game_id=new_game.id))
		else:
			flash("Please enter a URL.", category="error")

	return render_template("import_game.html", user=current_user)

@views.route('/link_players', methods=['GET','POST'])
@can_upload
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



	from time import sleep
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
		from botocore.exceptions import ClientError
		ledger_contents = []
		try:
			sleep(5)
			#r = requests.get(ledger_url, verify=False, timeout=10, stream=True)
			r = requests.get(ledger_url, verify=False, timeout=10)
			
			#for line in r.iter_lines():
			#	if line:
			#		ledger_contents.append(line.decode('UTF-8'))
			#import urllib.request
			#urllib.request.urlretrieve(ledger_url, 'website/static/uploads/ledgers/ledger_'+game_id+'.csv')
			#upload = s3.upload_file(
            #        Bucket = BUCKET_NAME,
            #        Filename='website/static/uploads/ledgers/ledger_'+game_id+'.csv',
            #        Key = 'ledgers/ledger_'+game_id+'.csv'
            #    )
			if not isfile_s3('ledgers/ledger_'+game_id+'.csv'):
				s3_resource = boto3.Session().resource('s3')
				bucket = s3_resource.Bucket(BUCKET_NAME)
				#bucket.upload_fileobj(r.raw, 'ledgers/ledger_'+game_id+'.csv')
				import io
				bucket.upload_fileobj(io.BytesIO(r.content), 'ledgers/ledger_'+game_id+'.csv')
			r.raise_for_status()
		except ClientError as e: #(RuntimeError, TypeError, NameError):
			#print(RuntimeError,TypeError,NameError)
			print(ClientError)
			flash("There was an error loading importing the game1.", category="error")
			return render_template("import_game.html", user=current_user)
		if r.status_code != 200:
			flash("There was an error loading importing the game2.", category="error")
			return render_template("import_game.html", user=current_user)
	
		#####################################
		#GAME LOADED
		#####################################
		#print(r.raw.read())
		#print(ledger_contents)
		#return 0
		csv_dicts.append([{k: v for k, v in row.items()} for row in csv.DictReader(r.text.splitlines(), skipinitialspace=True)])
		#csv_dicts.append([{k: v for k, v in row.items()} for row in csv.DictReader(ledger_contents, skipinitialspace=True)])
	
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
	game_dates = []
	for dict in csv_dicts[0]:
		if dict['session_start_at'] != "":
			game_dates.append(dict['session_start_at'])
	game_date = game_dates[len(game_dates)-1]
	
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

	for debt in debts:
		#####################################
		#ADD TO EARNINGS TABLE
		#####################################
		new_earning = Earning(net=debt['net'],player_id=debt['player_id'],game_id=game.id)
		db.session.add(new_earning)

		#####################################
		#ADD ANY UNUSED ALIASES
		#####################################
		for alias in debt['player_nickname']:
			alias_lookup = Alias.query.filter_by(alias=alias).first()
			if not alias_lookup:
				#ADD TO ALIAS TABLE
				new_alias = Alias(alias=alias, player_id=debt['player_id'])
				db.session.add(new_alias)

		#####################################
		#ADD POKER NOW IDS TO DB
		#####################################
		#print(debt)
		for pn_id in debt['pn_player_id']:
			pnid_lookup = PokernowId.query.filter_by(pn_id=pn_id).first()
			if pnid_lookup:
				#DELETE EXISTING pnid
				db.session.delete(pnid_lookup)
				db.session.flush()
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
	urls = {}
	for game in games:
		for url in game.urls:
			if game.id in urls.keys():
				if url.imported == False:
					urls[game.id] = url.imported
			else:
				urls[game.id] = url.imported
	#print(urls)
			

	return render_template("games.html", user=current_user, games=games, imported=urls)


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
@admin_required
def delete_game():
	gameID = request.args.get('game_id')
	game = Game.query.filter_by(id=gameID).first()
	urls = Url.query.filter_by(game_id=gameID)
	payments = Payment.query.filter_by(game_id=gameID)
	earnings = Earning.query.filter_by(game_id=gameID)
	behaviors = Behavior.query.filter_by(game_id=gameID)
	bankrolls = Bankroll.query.filter_by(game_id=gameID)
	for url in urls:
		db.session.delete(url)
	for payment in payments:
		db.session.delete(payment)
	for earning in earnings:
		db.session.delete(earning)
	for bankroll in bankrolls:
		db.session.delete(bankroll)
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
		player = Player.query.filter_by(id=28).first()
		if player:
			earnings = Earning.query.filter_by(player_id=player.id).all()
			if earnings:
				for earning in earnings:
					#print(earning)
					net += earning.net
			
			#get behavior stats
			behaviors = Behavior.query.filter_by(player_id=player.id).all()
			#print(behaviors)
			#if handsPlayed == 0 else round((handsParticipated / handsPlayed * 100),2),
	return render_template("profile.html", user=current_user, player=player, net=net)
	


@views.route('/import_log', methods=['GET','POST'])
@login_required
@can_upload
def import_log():
	game_id = request.args.get('game_id')
	game = Game.query.filter_by(id=game_id).first()

	if request.method == 'POST':
		from werkzeug.utils import secure_filename
		from werkzeug.datastructures import  FileStorage
		files = request.files.getlist('file[]')
		#print(files)
		#for f in files:
		#	print(secure_filename(f.filename))
		#return True
		for f in files:

			#file_name = "website/static/uploads/logs/" + secure_filename(f.filename)
			
			urls = []
			for url in game.urls:
				if not url.imported:
					split_url = url.url.split('/')
					urls.append(split_url[-1])
			stripped_filename = f.filename.replace('poker_now_log_','').replace('.csv','')
			if stripped_filename in urls:
				#f.save(file_name)
				if not isfile_s3('logs/'+secure_filename(f.filename)):
					s3.upload_fileobj(f, BUCKET_NAME,
						Key = 'logs/'+secure_filename(f.filename)
					)
				#print('file uploaded successfully')

				ledger_url_s3 = "https://pokermanager.s3.amazonaws.com/logs/poker_now_log_"+stripped_filename+".csv"
				parsedLog = parse_log(ledger_url_s3)
				
				print(parsedLog)
				behavior = parseBehavior(parsedLog, game_id, stripped_filename)
				#for each in behavior:
				#	print(each)
				#if len(behavior) > 0:
				#	import os
				#	os.remove(file_name)
			else:
				flash("That file does not belong to this game or has already been uploaded.", category="error")





	#csv_file = "website\static\pn_short_log.csv"	#short log
	#csv_file = "website\static\poker_now_log_pgl7AD32cnWhunjM_Vp4O-u7a.csv"		#long log
	#csv_file = "website\static\poker_now_log_pgl1--avjXuaD_nuEtDcqij2V.csv"		
	#csv_file = "website\static\poker_now_log_pglZVVjn_1wHYovvDGk7NYaaf.csv"		#name switch log
	#parsedLog = parse_log(csv_file)
	
	#preFlopBehavior = parsePreflopBehavior(parsedLog, game_id)
	#print(parsedLog['players'])
	return render_template("import_log.html", user=current_user, game=game)



@can_upload
def parse_log(csv_file):
	import re
	import urllib
	response = urllib.request.urlopen(csv_file)
	data = response.read().decode('utf-8')
	csv_dicts = []
	#csv_file = csv.DictReader(open(csv_file))
	csv_file = csv.DictReader(data.splitlines())
	#print(csv_file)
	#return 0

	# Admin action regexes
	createGameRegex = '^The player "(.*) @ (.*)" created the game with a stack of (\d*(?:\.\d\d)?)'
	adminApprovedRegex = '^The admin approved the player "(.*) @ (.*)" participation with a stack of (\d*(?:\.\d\d)?)'
	seatRequestRegex = '^The player "(.*) @ (.*)" requested a seat.'
	playerJoinRegex = '^The player "(.*) @ (.*)" joined the game with a stack of (\d*(?:\.\d\d)?)'
	playerQuitRegex = '^The player "(.*) @ (.*)" quits the game with a stack of (\d*(?:\.\d\d)?)'
	sitStandRegex = '^The player "(.*) @ (.*)" (\w*)\s\w* with the stack of (\d*(?:\.\d\d)?)'
	updateStackRegex = '^The admin updated the player "(.*) @ (.*)" stack from (\d+) to (\d+).'

	# Hand regexes
	beginHandRegex = "^-- starting hand #(\d*)  \(([a-zA-Z'0-9\/ ]*)\).*"
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
	gameType = ""
	bigBlind = 0
	smallBlind = 0
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
		elif re.search(updateStackRegex, row['entry']):
			adminActions.append({
				'action': 'updatedStack',
				'player': re.findall(updateStackRegex, row['entry'])[0][0],
				'playerId': re.findall(updateStackRegex, row['entry'])[0][1],
				'from': float(re.findall(updateStackRegex, row['entry'])[0][2]),
				'to': float(re.findall(updateStackRegex, row['entry'])[0][3]),
				'at': row['at'],
				'order': row['order'],
				'originalEntry': row['entry']
			})
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
			game_search = re.findall(beginHandRegex, row['entry'])[0][1]
			if game_search == "No Limit Texas Hold'em":
				gameType = 'NLHE'
			elif game_search == "Pot Limit Omaha Hi":
				gameType = 'PLO'
			elif game_search == "Pot Limit Omaha Hi/Lo 8 or Better":
				gameType = 'PLO8'
			

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
			if re.findall(blindRegex, row['entry'])[0][2] == 'big':
				bigBlind = re.findall(blindRegex, row['entry'])[0][3]
			elif re.findall(blindRegex, row['entry'])[0][2] == 'small':
				smallBlind = re.findall(blindRegex, row['entry'])[0][3]
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
			alias = Alias.query.filter_by(alias=row['player']).first()
			if pokernow_id:
				players.append([row['player'],row['playerId'],pokernow_id.player_id])
			elif alias:
				players.append([row['player'],row['playerId'],alias.player_id])
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
		'unparsedLogEntries': unparsedLogEntries,
		'gameType' : gameType,
		'bigBlind' : bigBlind,
		'smallBlind' : smallBlind
	}

@can_upload
def parseBehavior(pokerGame, game_id, stripped_filename):
	colorsDark = ['rgba(0,129,0,1)','rgba(0,0,255,1)','rgba(255,0,0,1)','rgba(255,165,0,1)','rgba(128,0,128,1)','rgba(139,69,19,1)','rgba(0,0,0,1)', 'rgb(255,20,147,1)', 'rgba(47,79,79,1)']
	colorsLight = ['rgba(0,129,0,0.5)','rgba(0,0,255,0.5)','rgba(255,0,0,0.5)','rgba(255,165,0,0.5)','rgba(128,0,128,0.5)','rgba(139,69,19,0.5)','rgba(0,0,0,0.5)', 'rgb(255,20,147,0.5)', 'rgba(47,79,79,0.5)']
	
	hands = range(1,pokerGame['numberOfHands']+1)
	from datetime import datetime, timedelta
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
		handStart = ""
		handEnd = ""

		
		while handAction[i]['action'] != 'flop' and handAction[i]['action'] != 'collected':
			#print(handAction[i]['action'])
			preflopAction.append(handAction[i])
			i += 1
		
		street = 0
		preflopAggressor = None
		for action in handAction:
			if action['action'] in ['flop','turn','river']: street += 1
			if action['action'] == 'collected': street = 4

			if action['action'] == 'beginHand':
				handStart = action['at']
			if action['action'] == 'endHand':
				handEnd = action['at']

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
				#print(action)
	
		#game_date = datetime.strptime(game_date, "%Y-%m-%dT%H:%M:%SZ")
		#print(handStart)
		handStartDateTime = datetime(int(handStart[0:4]),int(handStart[5:7]),int(handStart[8:10]),int(handStart[11:13]),int(handStart[14:16]), int(handStart[17:19]), 0)
		handEndDateTime = datetime(int(handEnd[0:4]),int(handEnd[5:7]),int(handEnd[8:10]),int(handEnd[11:13]),int(handEnd[14:16]), int(handEnd[17:19]), 0)
		#print(hand, (handEndDateTime-handStartDateTime).total_seconds(), handStart, handEnd)

		#this is still called allPreflopAction but it has all hand action in it, consider fixing
		allPreflopAction.append({
			'hand':hand,
			'numPlayers': len(pokerGame['stacks'][hand-1]['stackSizes']),
			'preflopAggressor': preflopAggressor,
			'preflopAction':preflopAction,
			'flopAction':flopAction,
			'turnAction':turnAction,
			'riverAction':riverAction,
			'handDuration': (handEndDateTime-handStartDateTime).total_seconds()
			})
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
			'duration_played' : [0,0,0],
			
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
			'cbet_fold' : [0,0,0],
			'cbet_call_raise' : [0,0,0],
			'cbet_check_fold' : [0,0,0],
			'fold_cbet' : [0,0,0],
			'call_raise_cbet' : [0,0,0],
			'2barrel' : [0,0,0],
			'2barrel_check_fold' : [0,0,0],
			'fold_2b' : [0,0,0],
			'call_raise_2b' : [0,0,0],
			'3barrel' : [0,0,0],
			'3barrel_check_fold' : [0,0,0],
			'fold_3b' : [0,0,0],
			'call_raise_3b' : [0,0,0],
			'fold_3bet' : [0,0,0],
			'call_raise_3bet' : [0,0,0],
			'turns_played' : [0,0,0,0],
			'rivers_played' : [0,0,0,0],
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

	#print(allPlayerActions)
	allBehavior = []
	for hand in allPreflopAction:

		#print(json.dumps(hand, indent=4))
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
		cbetCheckFold = []				# hands checked or folded on the flop when PFA (interrupted by donk)
		cbetFold = []					# hands folded to a cbet
		cbetCallRaise = []				# hands called or raised to a cbet

		turnPlayed = []					# turns seen
		barrel2 = []					# hands bet on turn after cbetting (interrupted by donk)
		barrel2CheckFold = []			# check or fold when given the opportunity to double barrel
		barrel2Fold = []				# hands folded to a double barrel
		barrel2CallRaise = []			# hands called or raised to a double barrel
		
		riverPlayed = []				# rivers seen
		barrel3 = []					# hands bet on turn after cbetting (interrupted by donk)
		barrel3CheckFold = []			# check or fold when given the opportunity to triple barrel
		barrel3Fold = []				# hands folded to a triple barrel
		barrel3CallRaise = []			# hands called or raised to a triple barrel
		
		bet3Fold = []					# hands folded to a 3 bet
		bet3CallRaise = []				# hands called or raised to a 3 bet
		wtsd = []						# hands made it to showdown

		lastAction = None
		last3Bet = False
		betCount = 1
		#preflop action
		for action in hand['preflopAction']:
			if action['player'] != None:
				preflopPlayed.append(action['player'])
			if action['action'] in ['raises to', 'bets']:
				preflopParticipated.append(action['player'])
				preflopRaised.append(action['player'])
				preflopAggressor = action['player']
				betCount += 1
			elif action['action'] in ['calls', 'straddles']:
				preflopParticipated.append(action['player'])
			
			#reaction to 3 bet
			if action['action'] == 'folds' and betCount == 3:
				bet3Fold.append(action['player'])
			elif action['action'] == 'raises to' and betCount == 3:
				bet3CallRaise.append(action['player'])

			#3 bet
			if lastAction == 'raises to' and action['action'] == 'raises to' and betCount == 3:
				preflop3bet.append(action['player'])
				#last3Bet = True
			elif lastAction == 'raises to' and action['action'] != 'raises to' and betCount == 2:
				preflopNo3bet.append(action['player'])

			#4 bet
			elif lastAction == 'raises to' and action['action'] == 'raises to' and betCount == 4:
				preflop4bet.append(action['player'])
			elif lastAction == 'raises to' and action['action'] != 'raises to' and betCount == 3:
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
			if action['action'] in ['checks','folds'] and action['player'] == preflopAggressor and lastAction not in ['bets','raises to','calls']:
				cbetCheckFold.append(action['player'])
			
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
			if action['action'] in ['checks','folds'] and action['player'] == preflopAggressor and lastCBet and lastAction not in ['bets','raises to','calls']:
				barrel2CheckFold.append(action['player'])
				
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
			if action['action'] in ['checks','folds'] and action['player'] == preflopAggressor and lastBarrel2 and lastAction not in ['bets','raises to','calls']:
				barrel3CheckFold.append(action['player'])

			if action['action'] == 'folds' and lastBarrel3:
				barrel3Fold.append(action['player'])
			if action['action'] in ['calls', 'raises to'] and lastBarrel3:
				barrel3CallRaise.append(action['player'])
			if action['action'] == 'folds':
				updatedShowdown = [value for value in showdownPlayers if value != action['player']]
				showdownPlayers = updatedShowdown
			lastAction = action['action']
		
		#showdown
		wtsd = showdownPlayers

		#run counts on each of the lists of names
		for each in [*set(preflopPlayed)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsPlayed'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['pre_handsPlayed'], hand['numPlayers'])
			allPlayerActions[findPlayerIndexByKey('names', each)]['duration_played'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['duration_played'], hand['numPlayers'], int(hand['handDuration']))
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
		for each in [*set(cbetCheckFold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['cbet_check_fold'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['cbet_check_fold'], hand['numPlayers'])
		for each in [*set(cbetFold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['fold_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['fold_cbet'], hand['numPlayers'])
		for each in [*set(cbetCallRaise)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_cbet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_cbet'], hand['numPlayers'])
			
		for each in [*set(barrel2)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['2barrel'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['2barrel'], hand['numPlayers'])
		for each in [*set(barrel2CheckFold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['2barrel_check_fold'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['2barrel_check_fold'], hand['numPlayers'])
		for each in [*set(barrel2Fold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['fold_2b'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['fold_2b'], hand['numPlayers'])
		for each in [*set(barrel2CallRaise)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_2b'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_2b'], hand['numPlayers'])
			
		for each in [*set(barrel3)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['3barrel'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['3barrel'], hand['numPlayers'])
		for each in [*set(barrel3CheckFold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['3barrel_check_fold'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['3barrel_check_fold'], hand['numPlayers'])
		for each in [*set(barrel3Fold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['fold_3b'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['fold_3b'], hand['numPlayers'])
		for each in [*set(barrel3CallRaise)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_3b'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_3b'], hand['numPlayers'])

		for each in [*set(turnPlayed)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['turns_played'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['turns_played'], hand['numPlayers'])
		for each in [*set(riverPlayed)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['rivers_played'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['rivers_played'], hand['numPlayers'])
		
		for each in [*set(bet3Fold)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['fold_3bet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['fold_3bet'], hand['numPlayers'])
		for each in [*set(bet3CallRaise)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_3bet'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['call_raise_3bet'], hand['numPlayers'])
			
		for each in [*set(wtsd)]:
			allPlayerActions[findPlayerIndexByKey('names', each)]['wtsd'] = incrementCount(allPlayerActions[findPlayerIndexByKey('names', each)]['wtsd'], hand['numPlayers'])

	#for each in allPlayerActions:
	#	print(each)
	urls = Url.query.filter_by(game_id=game_id).all()
	which_url = None
	for i, url in enumerate(urls):
		if stripped_filename in url.url:
			which_url = i
	
	####################################################################################################################################################
	#####SEARCH LEDGER AGAIN FOR BUY IN/OUT/NET
	####################################################################################################################################################
	csv_dicts = []
	#####################################
	#GAME SETUP
	#####################################
	game_url = urls[which_url].url
	game_url_split = game_url.split('/')
	game_code = game_url_split[-1]
	ledger_url = game_url + '/ledger_' + game_code + '.csv'
	ledger_url_s3 = "https://pokermanager.s3.amazonaws.com/ledgers/ledger_"+game_code+".csv"
	
	#####################################
	#LOAD THE GAME, ERROR IF FAILED
	#####################################
	from time import sleep
	ledger_contents = []
	try:
		sleep(5)
		if not isfile_s3('ledgers/ledger_'+game_code+'.csv'):
			#r = requests.get(ledger_url, verify=False, timeout=10, stream=True)
			r = requests.get(ledger_url, verify=False, timeout=10)
			#for line in r.iter_lines():
			#	if line:
			#		ledger_contents.append(line.decode('UTF-8'))
			s3_resource = boto3.Session().resource('s3')
			bucket = s3_resource.Bucket(BUCKET_NAME)
			import io
			bucket.upload_fileobj(io.BytesIO(r.content), 'ledgers/ledger_'+game_id+'.csv')
			#bucket.upload_fileobj(r.raw, 'ledgers/ledger_'+game_id+'.csv')
		else:
			#r = requests.get(ledger_url_s3, verify=False, timeout=10, stream=True)
			r = requests.get(ledger_url_s3, verify=False, timeout=10)
			#for line in r.iter_lines():
			#	if line:
			#		ledger_contents.append(line.decode('UTF-8'))
		r.raise_for_status()
	except: #(RuntimeError, TypeError, NameError):
		#print('error')
		flash("There was an error loading loading the ledger.", category="error")
		return render_template("import_log.html", user=current_user)
	if r.status_code != 200:
		flash("There was an error loading importing the game2.", category="error")
		return render_template("import_log.html", user=current_user)
	
	#csv_file = open('website/static/uploads/ledgers/ledger_'+game_code+'.csv', 'r')
	
	#####################################
	#GAME LOADED
	#####################################

	csv_dicts.append([{k: v for k, v in row.items()} for row in csv.DictReader(r.text.splitlines(), skipinitialspace=True)])
	#csv_dicts.append([{k: v for k, v in row.items()} for row in csv.DictReader(ledger_contents, skipinitialspace=True)])
	#csv_dicts.append([{k: v for k, v in row.items()} for row in csv.DictReader(csv_file, skipinitialspace=True)])
		
	#####################################
	#LOOP OVER CSV FILE AND PLACE INTO DICTIONARY
	#####################################
	game_dates = []
	for dict in csv_dicts[0]:
		if dict['session_start_at'] != "":
			game_dates.append(dict['session_start_at'])
	game_date = game_dates[len(game_dates)-1]

	def findPlayerIndexByKeyLog(PNDictionary, key, val):
		for i, dic in enumerate(PNDictionary):
			if isinstance(dic[key], list):
				if val in dic[key]:
					return i
			else:
				if val == dic[key]:
					return i
		return -1

	PNDictionary = []
	for each_dict in csv_dicts:
		for row in each_dict:
			playerIndex = findPlayerIndexByKeyLog(PNDictionary, 'pn_player_id', row['player_id'])
			if playerIndex >= 0:
				#player ID exists, add to it
				PNDictionary[playerIndex]['net'] += int(row['net'])
				PNDictionary[playerIndex]['buy_in'] += int(row['buy_in'])
				PNDictionary[playerIndex]['cash_out'] += int(row['buy_in']) + int(row['net'])
				if row['player_nickname'] not in PNDictionary[playerIndex]['player_nickname']:
					PNDictionary[playerIndex]['player_nickname'].append(row['player_nickname'])
			else:
				#add new player
				PNDictionary.append({
					'pn_player_id': [row['player_id']],
					'player_nickname': [row['player_nickname']],
					'net' : float(row['net']),
					'buy_in' : float(row['buy_in']),
					'cash_out' : float(row['buy_in']) + float(row['net']),
					'player_id' : None
					})
	#####################################
	#LOOP OVER THE DEBT DICT TO MATCH DATABASE PLAYERS OR SUBMITTED DATA
	#####################################
	for x,debt in enumerate(PNDictionary):
		#print(debt)
		pokernow_id = PokernowId.query.filter_by(pn_id=debt['pn_player_id'][0]).first()
		alias = Alias.query.filter_by(alias=debt['player_nickname'][0]).first()
		if pokernow_id:
			debt['player_id'] = pokernow_id.player_id
		elif alias:
			debt['player_id'] = alias.player_id
		else:
			debt['player_id'] = None

	#print(PNDictionary)
	finalLedger = []
	for debt in PNDictionary:
		playerIndex = findPlayerIndexByKeyLog(finalLedger, 'player_id', debt['player_id'])
		if playerIndex >= 0:
			for eachID in debt['pn_player_id']:
				if eachID not in finalLedger[playerIndex]['pn_player_id']:
					finalLedger[playerIndex]['pn_player_id'].append(eachID)
			
			for eachNickname in debt['player_nickname']:
				if eachNickname not in finalLedger[playerIndex]['player_nickname']:
					finalLedger[playerIndex]['player_nickname'].append(eachNickname)
			finalLedger[playerIndex]['net'] += debt['net']
			finalLedger[playerIndex]['buy_in'] += debt['buy_in']
			finalLedger[playerIndex]['cash_out'] += debt['cash_out']
		else:
			finalLedger.append(debt)
	#print('break')
	#print(finalLedger)
	from datetime import datetime, timedelta
	#print(csv_dicts[0][0])
	game_date_utc = datetime(int(game_date[0:4]),int(game_date[5:7]),int(game_date[8:10]),int(game_date[11:13]),int(game_date[14:16]), 0, 0)
	delta = timedelta(hours=9)
	game_date_est = game_date_utc - delta

	for eachLedger in finalLedger:
		#####################################
		#ADD BANKROLL RECORDS
		#####################################
		bankroll = Bankroll.query.filter_by(game_id=game_id, url_id=urls[which_url].id, player_id=eachLedger['player_id']).first()
		if not bankroll:
			new_bankroll = Bankroll(
				game_id=game_id,
				url_id=urls[which_url].id,
				date=game_date_est,
				player_id=eachLedger['player_id'],
				buyin=eachLedger['buy_in'],
				cashout=eachLedger['cash_out'],
				net=eachLedger['net'],
				imported=False,
				location='PokerNow'
			)
			db.session.add(new_bankroll)
	db.session.flush()

	for eachPlayer in allPlayerActions:
		#print(eachPlayer)
		if eachPlayer['player_id']:
			behavior = Behavior.query.filter_by(player_id=eachPlayer['player_id'],game_id=game_id).all()
			if not behavior:
				new_behavior = Behavior(
					game_id=game_id,
					url_id=urls[which_url].id,
					player_id=eachPlayer['player_id'],
					hu_duration_played = eachPlayer['duration_played'][0],
					sr_duration_played = eachPlayer['duration_played'][1],
					ft_duration_played = eachPlayer['duration_played'][2],

					hu_pre_hands_played = eachPlayer['pre_handsPlayed'][0],
					hu_pre_hands_participated = eachPlayer['pre_handsParticipated'][0],
					hu_pre_hands_raised = eachPlayer['pre_handsRaised'][0],
					hu_post_hands_played = eachPlayer['post_hands_played'][0],
					hu_post_hands_bet_raise = eachPlayer['post_hands_bet_raise'][0],
					hu_post_hands_call = eachPlayer['post_hands_call'][0],
					hu_post_hands_check = eachPlayer['post_hands_check'][0],
					hu_cbet = eachPlayer['cbet'][0],
					hu_cbet_check_fold = eachPlayer['cbet_check_fold'][0],
					hu_cbet_fold = eachPlayer['cbet_fold'][0],
					hu_cbet_call_raise = eachPlayer['cbet_call_raise'][0],
					hu_turns_played = eachPlayer['turns_played'][0],
					hu_rivers_played = eachPlayer['rivers_played'][0],
					hu_2barrel = eachPlayer['2barrel'][0],
					hu_2barrel_check_fold = eachPlayer['2barrel_check_fold'][0],
					hu_3barrel = eachPlayer['3barrel'][0],
					hu_3barrel_check_fold = eachPlayer['3barrel_check_fold'][0],
					hu_3bet = eachPlayer['3bet'][0],
					hu_no_3bet = eachPlayer['no_3bet'][0],
					hu_4bet = eachPlayer['4bet'][0],
					hu_no_4bet = eachPlayer['no_4bet'][0],
					hu_fold_cbet = eachPlayer['fold_cbet'][0],
					hu_call_raise_cbet = eachPlayer['call_raise_cbet'][0],
					hu_fold_2b = eachPlayer['fold_2b'][0],
					hu_call_raise_2b = eachPlayer['call_raise_2b'][0],
					hu_fold_3b = eachPlayer['fold_3b'][0],
					hu_call_raise_3b = eachPlayer['call_raise_3b'][0],
					hu_fold_3bet = eachPlayer['fold_3bet'][0],
					hu_call_raise_3bet = eachPlayer['call_raise_3bet'][0],
					hu_wtsd = eachPlayer['wtsd'][0],

					sr_pre_hands_played = eachPlayer['pre_handsPlayed'][1],
					sr_pre_hands_participated = eachPlayer['pre_handsParticipated'][1],
					sr_pre_hands_raised = eachPlayer['pre_handsRaised'][1],
					sr_post_hands_played = eachPlayer['post_hands_played'][1],
					sr_post_hands_bet_raise = eachPlayer['post_hands_bet_raise'][1],
					sr_post_hands_call = eachPlayer['post_hands_call'][1],
					sr_post_hands_check = eachPlayer['post_hands_check'][1],
					sr_cbet = eachPlayer['cbet'][1],
					sr_cbet_check_fold = eachPlayer['cbet_check_fold'][1],
					sr_cbet_fold = eachPlayer['cbet_fold'][1],
					sr_cbet_call_raise = eachPlayer['cbet_call_raise'][1],
					sr_turns_played = eachPlayer['turns_played'][1],
					sr_rivers_played = eachPlayer['rivers_played'][1],
					sr_2barrel = eachPlayer['2barrel'][1],
					sr_2barrel_check_fold = eachPlayer['2barrel_check_fold'][1],
					sr_3barrel = eachPlayer['3barrel'][1],
					sr_3barrel_check_fold = eachPlayer['3barrel_check_fold'][1],
					sr_3bet = eachPlayer['3bet'][1],
					sr_no_3bet = eachPlayer['no_3bet'][1],
					sr_4bet = eachPlayer['4bet'][1],
					sr_no_4bet = eachPlayer['no_4bet'][1],
					sr_fold_cbet = eachPlayer['fold_cbet'][1],
					sr_call_raise_cbet = eachPlayer['call_raise_cbet'][1],
					sr_fold_2b = eachPlayer['fold_2b'][1],
					sr_call_raise_2b = eachPlayer['call_raise_2b'][1],
					sr_fold_3b = eachPlayer['fold_3b'][1],
					sr_call_raise_3b = eachPlayer['call_raise_3b'][1],
					sr_fold_3bet = eachPlayer['fold_3bet'][1],
					sr_call_raise_3bet = eachPlayer['call_raise_3bet'][1],
					sr_wtsd = eachPlayer['wtsd'][1],

					ft_pre_hands_played = eachPlayer['pre_handsPlayed'][2],
					ft_pre_hands_participated = eachPlayer['pre_handsParticipated'][2],
					ft_pre_hands_raised = eachPlayer['pre_handsRaised'][2],
					ft_post_hands_played = eachPlayer['post_hands_played'][2],
					ft_post_hands_bet_raise = eachPlayer['post_hands_bet_raise'][2],
					ft_post_hands_call = eachPlayer['post_hands_call'][2],
					ft_post_hands_check = eachPlayer['post_hands_check'][2],
					ft_cbet = eachPlayer['cbet'][2],
					ft_cbet_check_fold = eachPlayer['cbet_check_fold'][2],
					ft_cbet_fold = eachPlayer['cbet_fold'][2],
					ft_cbet_call_raise = eachPlayer['cbet_call_raise'][2],
					ft_turns_played = eachPlayer['turns_played'][2],
					ft_rivers_played = eachPlayer['rivers_played'][2],
					ft_2barrel = eachPlayer['2barrel'][2],
					ft_2barrel_check_fold = eachPlayer['2barrel_check_fold'][2],
					ft_3barrel = eachPlayer['3barrel'][2],
					ft_3barrel_check_fold = eachPlayer['3barrel_check_fold'][2],
					ft_3bet = eachPlayer['3bet'][2],
					ft_no_3bet = eachPlayer['no_3bet'][2],
					ft_4bet = eachPlayer['4bet'][2],
					ft_no_4bet = eachPlayer['no_4bet'][2],
					ft_fold_cbet = eachPlayer['fold_cbet'][2],
					ft_call_raise_cbet = eachPlayer['call_raise_cbet'][2],
					ft_fold_2b = eachPlayer['fold_2b'][2],
					ft_call_raise_2b = eachPlayer['call_raise_2b'][2],
					ft_fold_3b = eachPlayer['fold_3b'][2],
					ft_call_raise_3b = eachPlayer['call_raise_3b'][2],
					ft_fold_3bet = eachPlayer['fold_3bet'][2],
					ft_call_raise_3bet = eachPlayer['call_raise_3bet'][2],
					ft_wtsd = eachPlayer['wtsd'][2],
				)
				db.session.add(new_behavior)
				db.session.flush()

				#update bankroll
				bankroll = Bankroll.query.filter_by(game_id=game_id, player_id=eachPlayer['player_id']).first()
				bankroll.behavior_id = Behavior.query.filter_by(url_id=urls[which_url].id, player_id=eachPlayer['player_id']).first().id
				bankroll.duration=sum(eachPlayer['duration_played'])
				bankroll.hands_played=sum(eachPlayer['pre_handsPlayed'])

	
	

	
	urls[which_url].imported = True
	if pokerGame['gameType']: urls[which_url].game_type = pokerGame['gameType']
	if pokerGame['bigBlind']: urls[which_url].big_blind = pokerGame['bigBlind']
	if pokerGame['smallBlind']: urls[which_url].small_blind = pokerGame['smallBlind']
	#for eachAction in pokerGame['adminActions']:
	#	print(eachAction)
	#print(pokerGame['adminActions'])
	db.session.commit()

	return allPlayerActions


@views.route('/player_stats', methods=['GET','POST'])
@login_required
@sub_required
def player_stats():
	user=current_user
	player=null
	if user.player_id:
		player = Player.query.filter_by(id=user.player_id).first()
		if user.admin:
			#player = Player.query.filter_by(id=28).first()	#MG
			#player = Player.query.filter_by(id=13).first()	#Fluffy
			#player = Player.query.filter_by(id=14).first()	#Gocha
			#player = Player.query.filter_by(id=20).first()	#Josh
			#player = Player.query.filter_by(id=38).first()	#Sean
			print(player)


		if request.method == 'POST':
			nlhe = request.form.get('filter_nlhe')
			plo = request.form.get('filter_plo')
			plo8 = request.form.get('filter_plo8')
			game_type_filter = []
			if nlhe: game_type_filter.append('NLHE')
			if plo: game_type_filter.append('PLO')
			if plo8: game_type_filter.append('PLO8')
		else:
			nlhe = True
			plo = True
			plo8 = True
			game_type_filter = ['NLHE', 'PLO', 'PLO8']
		
		if player:
			#get behavior stats
			#bankrolls = Bankroll.query.order_by(Bankroll.date.desc()).filter_by(player_id=player.id).all()
			bankrolls = Bankroll.query.order_by(Bankroll.date.desc()).filter_by(player_id=player.id).filter(Bankroll.url.has(Url.game_type.in_(game_type_filter))).all()
			
			player_behavior = {
				'pre_hands_played' : [0,0,0,0],
				'pre_hands_participated' : [0,0,0,0],
				'pre_hands_raised' : [0,0,0,0],
				'post_hands_played' : [0,0,0,0],
				'post_hands_bet_raise' : [0,0,0,0],
				'post_hands_call' : [0,0,0,0],
				'post_hands_check' : [0,0,0,0],
				'cbet' : [0,0,0,0],
				'cbet_check_fold' : [0,0,0,0],
				'cbet_fold' : [0,0,0,0],
				'cbet_call_raise' : [0,0,0,0],
				'turns_played' : [0,0,0,0],
				'rivers_played' : [0,0,0,0],
				'2barrel' : [0,0,0,0],
				'2barrel_check_fold' : [0,0,0,0],
				'3barrel' : [0,0,0,0],
				'3barrel_check_fold' : [0,0,0,0],
				'3bet' : [0,0,0,0],
				'no_3bet' : [0,0,0,0],
				'4bet' : [0,0,0,0],
				'no_4bet' : [0,0,0,0],
				'fold_cbet' : [0,0,0,0],
				'call_raise_cbet' : [0,0,0,0],
				'fold_2b' : [0,0,0,0],
				'call_raise_2b' : [0,0,0,0],
				'fold_3b' : [0,0,0,0],
				'call_raise_3b' : [0,0,0,0],
				'fold_3bet' : [0,0,0,0],
				'call_raise_3bet' : [0,0,0,0],
				'wtsd' : [0,0,0,0],
				'duration_played' : [0,0,0,0],
				}
			
			for bankroll in bankrolls:
				if bankroll.behavior:
					for each_behavior in player_behavior.keys():
						#print(each_behavior)
						x = eval('bankroll.behavior.hu_'+each_behavior)
						y = eval('bankroll.behavior.sr_'+each_behavior)
						z = eval('bankroll.behavior.ft_'+each_behavior)
						player_behavior[each_behavior][0] += x
						player_behavior[each_behavior][1] += y
						player_behavior[each_behavior][2] += z
						player_behavior[each_behavior][3] += x+y+z

			#print(player_behavior)
			bankrollChartX = []
			bankrollChartY = []
			winslosses = [0,0]
			for bankroll in bankrolls:
				if bankroll.net > 0:
					winslosses[0] += 1
				elif bankroll.net < 0:
					winslosses[1] += 1
			bankrollNet = 0
			bankroll_reverse = bankrolls.copy()
			bankroll_reverse.reverse()
			for bankroll in bankroll_reverse:
				bankrollNet += bankroll.net
				bankrollChartY.append(bankrollNet)
				bankrollChartX.append(bankroll.date.strftime('%b %d, %y'))
			#print(round(pre_hands_participated[3]/pre_hands_played[3] * 100,2))
			#if handsPlayed == 0 else round((handsParticipated / handsPlayed * 100),2),
	return render_template("player_stats.html", user=current_user, player=player, pb=player_behavior, bankrolls=bankrolls, wl=winslosses, nlhe=nlhe, plo=plo, plo8=plo8, bankrollChartX=bankrollChartX, bankrollChartY=bankrollChartY)

@views.route('/delete_log', methods=['GET'])
@can_upload
def delete_log():
	urlID = request.args.get('url_id')
	
	url = Url.query.filter_by(id=urlID).first()
	behaviors = Behavior.query.filter_by(url_id=urlID).all()
	bankrolls = Bankroll.query.filter_by(url_id=urlID).all()
	url.imported = False
	for behavior in behaviors:
		db.session.delete(behavior)
	for bankroll in bankrolls:
		db.session.delete(bankroll)
	db.session.commit()
	#games = Game.query.all()
	#return render_template("games.html", user=current_user, games=games)
	return redirect(url_for('views.import_log', game_id=url.game_id))

@views.route('/batch_import_logs', methods=['GET','POST'])
@login_required
@can_upload
def batch_import_logs():
	#loop over the urls
	#if url log exists, run behavior
	#if ledger is missing, try to grab it and store to s3
	urls = Url.query.all()

	fileCheck = []
	for url in urls:
		behaviors = Behavior.query.filter_by(url_id=url.id).all()
		bankrolls = Bankroll.query.filter_by(url_id=url.id).all()
		url.imported = False
		for bankroll in bankrolls:
			db.session.delete(bankroll)
		for behavior in behaviors:
			db.session.delete(behavior)
		db.session.flush()

		stripped_filename = url.url.replace('https://www.pokernow.club/games/','')
		

		log_file_name = "https://pokermanager.s3.amazonaws.com/logs/poker_now_log_" + stripped_filename + '.csv'
		log_file_exists = isfile_s3('logs/poker_now_log_' + stripped_filename + '.csv')
		#if log_file_exists:
		#	s3.upload_file(
		#		Bucket = BUCKET_NAME,
		#		Filename=log_file_name,
		#		Key = 'logs/poker_now_log_' + stripped_filename + '.csv'
		#	)
			
		ledger_file_name = "https://pokermanager.s3.amazonaws.com/ledger_" + stripped_filename + '.csv'
		ledger_file_exists = isfile_s3('ledgers/ledger_' + stripped_filename + '.csv')
		#if ledger_file_exists:
		#	s3.upload_file(
		#		Bucket = BUCKET_NAME,
		#		Filename=ledger_file_name,
		#		Key = 'ledgers/ledger_' + stripped_filename + '.csv'
		#	)

		#print(log_file_name, log_file_exists, ledger_file_exists)

		if log_file_exists:
			parsedLog = parse_log(log_file_name)
			behavior = parseBehavior(parsedLog, url.game_id, stripped_filename)
		#else:
			##run the bankroll part of the log parsing
		fileCheck.append({
			'url': url.url,
			'ledger_exists': ledger_file_exists,
			'log_exists': log_file_exists
		})
	db.session.commit()
	s3_resource = boto3.resource('s3')
	my_bucket = s3_resource.Bucket(BUCKET_NAME)
	summaries = my_bucket.objects.all()
	return render_template('files.html', my_bucket=my_bucket, files=summaries, file_check=fileCheck)