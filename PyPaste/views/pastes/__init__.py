from flask import (
    abort,
    Blueprint,
    flash,
    make_response,
    redirect,
    request,
    render_template,
    session,
)

from PyPaste.utils import pypaste_url_for as url_for
from PyPaste.forms import NewPaste, PastePassword
from PyPaste.models.pastes import Paste

pastes = Blueprint('pastes', __name__, template_folder='templates')


@pastes.route('/', methods=['GET', 'POST'])
def index():
    form = NewPaste()
    if form.validate_on_submit():
        # WTForms passes '' for empty text values,
        # this lambda switches them to None
        f = lambda s: s if s != '' else None
        vals = {
            'text': form.paste.data,
            'title': f(form.title.data),
            'language': f(form.language.data),
            'password': f(form.password.data),
            'unlisted': f(form.unlisted.data)
        }
        paste = Paste.new(**vals)
        if paste is None:
            return redirect(url_for('pastes.index'))
        else:
            authorise_viewing(paste['hash'])
            if paste['unlisted']:
                url = url_for('pastes.unlisted', paste_hash=paste['hash'])
            else:
                url = url_for('pastes.public', paste_id=paste['id'])
            return redirect(url)
    elif request.method == 'POST':
        # Form submitted but failed validation
        for field, error in form.errors.items():
            errormsg = '{0}: {1}'.format(field, error[0])
            flash(errormsg, 'error')

    return render_template('index.html', form=form)


@pastes.route('/p/authorise', methods=['POST'])
def submit_password():
    form = PastePassword()
    if form.validate_on_submit():
        p_hash = form.paste_hash.data
        password = form.password.data

        if Paste.password_match(p_hash, password):
            # Password correct, add paste hash to authorised_pastes
            authorise_viewing(p_hash)
        else:
            # Todo: log & cap number of incorrect tries
            flash('Incorrect password', 'error')

        return redirect(form.redirect.data)
    else:
        return redirect(form.redirect.data)


@pastes.route('/p/<int:paste_id>/')
@pastes.route('/p/<int:paste_id>/<raw>/')
def public(paste_id, raw=None):
    return view_paste(False, paste_id, raw)


@pastes.route('/u/<paste_hash>/')
@pastes.route('/u/<paste_hash>/<raw>/')
def unlisted(paste_hash, raw=None):
    return view_paste(True, paste_hash, raw)


@pastes.route('/recent')
def recent():
    if session.get('logged_in'):
        pastes = Paste.recent(include_unlisted=True)
    else:
        pastes = Paste.recent()

    return render_template(
        'recent.html',
        pastes=pastes,
        title='recent pastes'
    )


def authorise_viewing(p_hash):
    if not 'authorised_pastes' in session:
        session['authorised_pastes'] = []

    session['authorised_pastes'].append(p_hash)
    session.modified = True


def view_paste(unlisted, attr, raw=None):
    if unlisted:
        paste = Paste.by_hash(attr)
    else:
        paste = Paste.by_id(attr)
        if paste is None or paste['unlisted']:
            abort(404)

    if paste is None:
        abort(404)

    # Check if paste is password protected, and if so,
    # whether the client is allowed to access it or not
    authorised = session.get('authorised_pastes', [])
    if (
        paste['password'] is not None and
        paste['hash'] not in authorised
    ):
        return render_template(
            'enter_password.html',
            paste=paste,
            form=PastePassword()
        ), 401

    if raw is not None:
        r = make_response(paste['text'])
        r.mimetype = 'text/plain'
        return r

    return render_template(
        'view_paste.html',
        title=paste['title'],
        paste=paste,
    )
