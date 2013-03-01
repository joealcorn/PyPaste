from flask import Blueprint

public = Blueprint('public', __name__, template_folder='templates')


@public.route('/')
def index():
    return 'Hello World'
