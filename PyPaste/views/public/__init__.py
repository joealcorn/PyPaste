from flask import Blueprint, render_template

from PyPaste.forms import NewPaste

public = Blueprint('public', __name__, template_folder='templates')


@public.route('/', methods=['GET', 'POST'])
def index():
    form = NewPaste()
    if form.validate_on_submit():
        return 'hello'
    return render_template('index.html', form=form)
