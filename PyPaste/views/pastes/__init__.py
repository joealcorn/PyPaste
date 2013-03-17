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
                url = url_for('pastes.unlisted', paste_hash=paste['hash'])
            else:
                url = url_for('pastes.public', paste_id=paste['id'])
            return redirect(url)

    return render_template('index.html', form=form)


@pastes.route('/p/<int:paste_id>/')
@pastes.route('/p/<int:paste_id>/<raw>/')
def public(paste_id, raw=None):
    return view_paste(False, paste_id, raw)


@pastes.route('/u/<paste_hash>/')
@pastes.route('/u/<paste_hash>/<raw>/')
def unlisted(paste_hash, raw=None):
    return view_paste(True, paste_hash, raw)


def view_paste(unlisted, attr, raw=None):
    if unlisted:
        paste = Paste.by_hash(attr)
    else:
        paste = Paste.by_id(attr)
        if paste['unlisted']:
            abort(404)

    if paste is None:
        abort(404)

    if raw is not None:
        r = make_response(paste['text'])
        r.mimetype = 'text/plain'
        return r

    return render_template('view_paste.html', paste=paste)
