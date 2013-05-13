"""
v1 PyPaste REST API.

Some weird things:
 - Flask doesn't do routing local to blueprints,
   so any errors registered here won't be used
   unless they're caused in a view (via abort).

   To work around this there is a catch-all route
   that will 404 if no other routes are matched.
   A consequence of this is all POST-only routes
   need to also accept GET to avoid returning a
   404 when GET is used.
   Use the post_only decorator to correctly return
   a JSON 405.

"""
from functools import wraps
from calendar import timegm

from flask import Blueprint, request, jsonify, abort, render_template

from PyPaste.utils import create_paste_url
from PyPaste.models.pastes import Paste

v1 = Blueprint(
    'v1',
    __name__,
    url_prefix='/api/v1',
    template_folder='templates'
)


def post_only(func):
    @wraps(func)
    def wrapper(*a, **kw):
        if request.method == 'GET':
            return abort(405)
        return func(*a, **kw)
    return wrapper


def create_paste_dict(paste):
    """
    Creates a dict representation of paste
    """
    return {
        'title': paste['title'],
        'text': paste['text'],
        'id': paste['id'],
        'hash': paste['hash'],
        'html': paste['highlighted'],
        'unlisted': paste['unlisted'],
        'created': timegm(paste['created'].timetuple()),
        'language': paste['language']
    }


@v1.route('/')
def docs():
    return render_template('docs.html', title='api')


@v1.route('/new', methods=['POST', 'GET'])
@post_only
def new():
    """
    Endpoint for creating a new paste.
    """
    form = request.form

    text = form.get('text')
    if text is None:
        return jsonify(error='required value missing: text'), 400

    unlisted = form.get('unlisted', 'f')
    if unlisted.lower() in ('1', 'true', 't', 'y'):
        unlisted = True
    else:
        unlisted = False

    paste = {
        'text': text,
        'title': form.get('title'),
        'language': form.get('lang', 'text'),
        'password': form.get('password'),
        'unlisted': unlisted,
    }

    p = Paste.new(**paste)
    if not Paste:
        return internal_server_error()

    response = {
        'url': create_paste_url(p),
        'shorturl': p['shortlink'],
        'paste': create_paste_dict(p),
        'password': paste['password'],
    }

    return jsonify(response)


@v1.route('/get')
def get():
    p_id = request.args.get('id', None, type=int)
    p_hash = request.args.get('hash', None)
    password = request.args.get('password')

    if p_hash:
        paste = Paste.by_hash(p_hash)
    elif p_id:
        paste = Paste.by_id(p_id)
    else:
        return jsonify(error='no id or hash supplied'), 400

    if paste is None:
        return jsonify(error='paste not found'), 404
    elif not p_hash and paste['unlisted']:
        return jsonify(error='paste is unlisted'), 400

    if paste['password']:
        if not password:
            return jsonify(error='paste is password protected'), 401
        elif not Paste.password_match(paste['hash'], password):
            return jsonify(error='incorrect password'), 401

    return jsonify(
        create_paste_dict(paste),
        shorturl=paste['shortlink'],
        url=create_paste_url(paste)
    )


@v1.errorhandler(404)
def not_found(error):
    return jsonify(error='resource not found'), 404


@v1.errorhandler(405)
def unsupported_method(error):
    return jsonify(error='unsupported http method'), 405


def internal_server_error():
    """
    It's not possible to register 500 in a blueprint,
    this function will need to be called directly
    """
    return jsonify(error='internal server error'), 500


@v1.route('/<path:path>')
def catchall(path):
    """
    This catches all undefined endpoints
    and responds with a JSON 404 resource
    """
    abort(404)
