from website import create_app

app = create_app()

def seconds_to_hours_minutes(seconds):
	N = int(seconds)
	min = 60
	hour = 60 * 60
	day = 60 * 60 * 24

	HOUR = N // hour
	MINUT = (N - (HOUR * hour)) // min
	SECONDS = N - ((HOUR * hour) + (MINUT * min))
	returnVal = str(HOUR)+":"+str(MINUT)
	return returnVal

def merge_behavior(behavior, stat):
	return eval('behavior.hu_'+stat) + eval('behavior.sr_'+stat) + eval('behavior.ft_'+stat)

def format_dollar(value):
	returnVal = ""
	if float(value).is_integer():
		if value < 0:
			returnVal = "-${:,}".format(abs(value))
		else:
			returnVal = "${:,}".format(value)
	else:
		if value < 0:
			returnVal = "-${:,.2f}".format(abs(value))
		else:
			returnVal = "${:,.2f}".format(value)
	return returnVal

app.jinja_env.globals.update(seconds_to_hours_minutes=seconds_to_hours_minutes)
app.jinja_env.globals.update(merge_behavior=merge_behavior)
app.jinja_env.globals.update(format_dollar=format_dollar)


if __name__ == '__main__':
	app.run(debug=True)