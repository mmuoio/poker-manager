from app import app, db
from .models import User, Player, Alias, Game, Payment, Url
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

manager = Manager(app)
migrate = Migrate(app,db)

manager.add_command('db', MigrateCommand)
manager.add_command('server', Server)

@manager.shell
def make_shell_context():
	return dict(app=app, db=db, Game=Game, User=User, Player=Player, Alias=Alias, Payment=Payment, Url=Url) # Add Game model to the dict

if __name__ == '__main__':
	manager.run()