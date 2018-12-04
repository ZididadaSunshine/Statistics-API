import os

from flask_cors import CORS
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import blueprint
from app.main import create_app, db

app = create_app(os.getenv('API_CONFIG', 'dev'))
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.register_blueprint(blueprint)

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def run():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    run()
