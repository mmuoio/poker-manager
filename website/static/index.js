function deleteNote(noteId){
	fetch('/delete-note', {
		method: 'POST',
		body: JSON.stringify({noteId: noteId}),
	}).then((_res) => {
		window.location.href = '/';
	});
}

function deleteAlias(aliasId, player_id){
	fetch('/delete-alias', {
		method: 'POST',
		body: JSON.stringify({aliasId: aliasId}),
	}).then((_res) => {
		window.location.href = '/edit_player?player_id='+player_id;
	});
}

 function exportSettlement(gameID){
	//window.location.href = '/export_settlement?game_id='+gameID;
	url = '/export_settlement?game_id='+gameID
 	fetch(url)
	
}

function expireSub(userID){
	fetch('/expire_sub', {
		method: 'POST',
		body: JSON.stringify({userID: userID}),
	}).then((_res) => {
		window.location.href = '/manage_users';
	});
}

function add30Days(userID){
	fetch('/add_30_days', {
		method: 'POST',
		body: JSON.stringify({userID: userID}),
	}).then((_res) => {
		window.location.href = '/manage_users';
	});
}