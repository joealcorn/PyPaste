from subprocess import check_output

from flask import Flask, url_for, request, redirect


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
from PyPaste.views.admin import admin
from PyPaste.views import api

app.register_blueprint(errors)
app.register_blueprint(pastes)
app.register_blueprint(admin)
app.register_blueprint(api.legacy)
app.register_blueprint(api.v1)


# This allows us to enforce the FORCE_SSL config option
# Any redirection should be done at the httpd level
from PyPaste.utils import pypaste_url_for

@app.context_processor
def override_url_for():
    return dict(url_for=pypaste_url_for)
