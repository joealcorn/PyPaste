from flask import Blueprint, render_template

errors = Blueprint('errors', __name__, template_folder='templates')


@errors.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404
