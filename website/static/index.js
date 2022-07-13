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

