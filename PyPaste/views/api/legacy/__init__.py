"""
This file ensures compatibility with the few clients
that actually do use the existing API.

"""

from flask import Blueprint, request, jsonify

from PyPaste.utils import create_paste_url
from PyPaste.models.pastes import Paste

legacy = Blueprint('legacy', __name__)


@legacy.route('/api/add', methods=['POST'])
def add():
    form = request.form
    errors = []

    if form.get('unlisted', type=int) in (0, 1):
        unlisted = bool(form.get('unlisted', type=int))
    else:
        unlisted = False

    paste = {
        'text': form.get('contents'),
        'title': form.get('title'),
        'password': form.get('password'),
        'unlisted': unlisted,
        'language': form.get('language', 'text')
    }

    if paste['text'] is None:
        errors.append('No contents specified')
    if paste['unlisted'] not in (True, False):
        errors.append(
            "Invalid value: (unlisted: '{0}')".format(paste['unlisted'])
        )

    if errors:
        return jsonify(
            success=False,
            url=None,
            password=None,
            error=errors
        )

    p = Paste.new(**paste)
    if p is None:
        return jsonify(
            success=False,
            url=None,
            password=None,
            error=errors
        )

    return jsonify(
        success=True,
        url=create_paste_url(p),
        password=paste['password']
    )
