from subprocess import check_output

from flask import Flask


def get_version():
    try:
        return check_output('git rev-parse HEAD', shell=True)
    except:
        return None

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['VERSION'] = get_version()

from PyPaste.models.pastes import Paste
from PyPaste.models.users import User

Paste.init_table()
User.init_table()

from PyPaste.views.errors import errors
from PyPaste.views.pastes import pastes
from PyPaste.views import api

app.register_blueprint(errors)
app.register_blueprint(pastes)
app.register_blueprint(api.legacy)
