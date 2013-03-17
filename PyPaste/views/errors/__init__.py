from flask import render_template

from PyPaste import app


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html', title='404'), 404
