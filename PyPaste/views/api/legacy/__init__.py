"""
This file ensures compatibility with the few clients
that actually do use the existing API.

"""

from flask import Blueprint, request, jsonify, url_for

from PyPaste.models.pastes import Paste

legacy = Blueprint('legacy', __name__)


@legacy.route('/api/add', methods=['POST'])
def add():
    form = request.form
    errors = []

    if form.get('unlisted') in ('0', '1'):
        unlisted = bool(int(form.get('unlisted')))
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

    if p['unlisted']:
        url = url_for(
            'pastes.unlisted',
            paste_hash=p['hash'],
            _external=True
        )
    else:
        url = url_for(
            'pastes.public',
            paste_id=p['id'],
            _external=True
        )

    return jsonify(
        success=True,
        url=url,
        password=paste['password']
    )
