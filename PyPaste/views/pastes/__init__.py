from flask import (
    abort,
    Blueprint,
    make_response,
    redirect,
    render_template,
    url_for
)

from PyPaste.forms import NewPaste
from PyPaste.models.pastes import Paste

pastes = Blueprint('pastes', __name__, template_folder='templates')


@pastes.route('/', methods=['GET', 'POST'])
def index():
    form = NewPaste()
    if form.validate_on_submit():
        # WTForms passes '' for empty text values,
        # this lamba switches them to None
        f = lambda s: s if s != '' else None
        vals = {
            'text': form.text.data,
            'title': f(form.title.data),
            'language': f(form.language.data),
            'password': f(form.password.data),
            'unlisted': f(form.unlisted.data)
        }
        paste = Paste.new(**vals)
        if paste is None:
            return redirect(url_for('pastes.index'))
        else:
            if paste['unlisted']:
                url = url_for('pastes.view_unlisted', paste_hash=paste['hash'])
            else:
                url = url_for('pastes.view_paste', paste_id=paste['id'])
            return redirect(url)

    return render_template('index.html', form=form)


@pastes.route('/p/<int:paste_id>/')
@pastes.route('/p/<int:paste_id>/<raw>/')
def view_paste(paste_id, raw=None):
    paste = Paste.by_id(paste_id)
    if paste is None or paste['unlisted']:
        abort(404)

    if raw is not None:
        return text_response(paste['text'])

    return render_template('view_paste.html', paste=paste)


@pastes.route('/u/<paste_hash>/')
@pastes.route('/u/<paste_hash>/<raw>/')
def view_unlisted(paste_hash, raw=None):
    paste = Paste.by_hash(paste_hash)
    if paste is None:
        abort(404)

    if raw is not None:
        return text_response(paste['text'])

    return render_template('view_paste.html', paste=paste)


def text_response(text):
    resp = make_response(text)
    resp.mimetype = 'text/plain'
    return resp
