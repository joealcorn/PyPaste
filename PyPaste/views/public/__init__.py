from flask import Blueprint, render_template, redirect, url_for

from PyPaste.forms import NewPaste
from PyPaste.models.pastes import Paste

public = Blueprint('public', __name__, template_folder='templates')


@public.route('/', methods=['GET', 'POST'])
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
            return redirect(url_for('public.index'))
        else:
            # Will redirect to paste page when it's implemented
            return str(paste['id'])

    return render_template('index.html', form=form)
