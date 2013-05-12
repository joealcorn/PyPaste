from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    abort,
    redirect,
)

from PyPaste.utils import pypaste_url_for as url_for
from PyPaste.forms import LoginForm, LogoutForm, DeletePasteForm
from PyPaste.models.users import User
from PyPaste.models.pastes import Paste

admin = Blueprint(
    'admin',
    __name__,
    url_prefix='/a',
    template_folder='templates'
)


def login_required(func):
    """
    Decorator that ensures a user
    is logged in before accessing
    a view, else throws up a 401

    """
    @wraps(func)
    def wrapper(*a, **kw):
        if not session.get('logged_in'):
            abort(401)
        return func(*a, **kw)
    return wrapper


@admin.route('/in', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.password_match(username, password):
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('pastes.index'))
        else:
            flash('Incorrect username/password', 'error')

    return render_template('login.html', form=form)


@admin.route('/out', methods=['GET', 'POST'])
@login_required
def logout():
    form = LogoutForm()
    if request.method == 'POST' and form.validate_on_submit():
        if session.get('username') == form.username.data:
            session.pop('username')
            session.pop('logged_in')
            session.modified = True
            return redirect(url_for('pastes.index'))

    return render_template('logout.html', form=form)


@admin.route('/del/<hash>', methods=['GET', 'POST'])
@login_required
def delete_paste(hash):
    form = DeletePasteForm()
    if form.validate_on_submit():
        if not Paste.delete(form.paste_hash.data):
            flash('Deletion failed', 'error')
            return redirect(request.url)

        return redirect(url_for('pastes.recent'))

    return render_template('delete.html', form=form, hash=hash)
