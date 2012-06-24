from datetime import datetime
import hashlib
import random

from flask import Flask, redirect, url_for, render_template, flash, request, abort, jsonify, session
from flask.ext.sqlalchemy import SQLAlchemy

import highlight
import pretty_age

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

class pastes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posted = db.Column(db.DateTime)
    title = db.Column(db.String(50))
    contents = db.Column(db.Text)
    password = db.Column(db.String(20))
    language = db.Column(db.String(40))
    unlisted = db.Column(db.Integer(16))
    p_hash = db.Column(db.String(6))

    def __init__(self, title, contents, password, language, unlisted, p_hash):
        self.posted = datetime.now()
        self.title = title
        self.contents = contents
        self.password = password
        self.language = language
        self.unlisted = unlisted
        self.p_hash = p_hash

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

def hashPassword(password):
    p = hashlib.new('sha256')
    p.update(password + app.config['SECRET_KEY'])
    return p.hexdigest()

def addPaste(title, contents, password, language, unlisted, p_hash):
    if title.strip() == '':
        title = "Untitled"
    p = pastes(title, contents, password, language, unlisted, p_hash)
    db.session.add(p)
    db.session.commit()
    return p

def delPaste(id):
    p = pastes.query.get(id)
    db.session.delete(p)
    db.session.commit()
    return p

def generatePasteHash():
    ''' Generates a unique sequence to identify a paste,
        used for unlisted pastes'''
    while True:
        p_hash = str(random.getrandbits(50))[:7]
        otherPastes = pastes.query.filter_by(p_hash=p_hash).order_by(pastes.posted.desc()).all()
        if otherPastes == []:
            break
    return p_hash

@app.route('/add', methods=['POST', 'GET'])
def add():
    r = request
    if r.method == 'GET':
        return redirect(url_for('index'))
    if r.form['contents'].strip() == '':
        flash('You need to paste some text')
        return redirect(url_for('index'))
    p_hash = generatePasteHash()

    p = addPaste(r.form['title'], r.form['contents'], None, r.form['language'], r.form['unlisted'], p_hash)

    if r.form['unlisted'] == '1':
        flash('Unlisted paste created! It can only be accessed via this URL, so be careful who you share it with')
        return redirect(url_for('view_unlisted_paste', paste_hash=p.p_hash))
    else:
        return redirect(url_for('view_paste', paste_id=p.id))

@app.route('/del', methods=['POST'])
def delete():
    if 'logged_in' not in session.keys() or session['logged_in'] != True:
        abort(401)
    r = request
    delPaste(r.form['pid'])
    flash('Paste with ID #%s has been deleted' % r.form['pid'])
    return redirect(url_for('view_all_pastes'))


@app.route('/authenticate', methods=['POST'])
def login():
    r = request
    password = hashPassword(r.form['password'])
    u = users.query.filter_by(username=r.form['username']).first()
    if u == None or u.password != password:
        flash('Login failed')
        return redirect(url_for('loginPage'))
    else:
        session['logged_in'] = True
        flash('Successfully logged in')
        return redirect(url_for('index'))

# Pages

@app.route('/')
def index():
    error = None
    _pastes = pastes.query.filter_by(unlisted=0).order_by(pastes.posted.desc()).limit(7).all()
    for thing in _pastes:
        thing.posted = pretty_age.get_age(thing.posted)
    return render_template('add_paste.html', pastes=_pastes, error=error)

@app.route('/login/')
def loginPage():
    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/view/')
def view_list():
    error = None
    _pastes = pastes.query.filter_by(unlisted=0).order_by(pastes.posted.desc()).limit(40).all()
    for thing in _pastes:
        thing.posted = pretty_age.get_age(thing.posted)
    return render_template('paste_list.html', pastes=_pastes, error=error)

@app.route('/view/<int:paste_id>/')
def view_paste(paste_id):
    error = None
    highlighted = None
    cur_paste = pastes.query.get(paste_id)
    if cur_paste == None or cur_paste.unlisted == 1:
        abort(404)
    try: highlighted = highlight.syntax(cur_paste.contents, cur_paste.language)
    except:
        ''' In the case where the user was able to select a language which has no syntax highlighting configured
            (by sending a POST request and not using the form) it will alert them to it '''
        error = 'That language has no highlighting available! Oops! <a href="mailto://%(email)s">email</a> me and tell me to fix it!' % { 'email': app.config['EMAIL'] }
        highlighted = highlight.syntax(cur_paste.contents, 'none')
    recent_pastes = pastes.query.filter_by(unlisted=0).order_by(pastes.posted.desc()).limit(7).all()
    for thing in recent_pastes:
        thing.posted = pretty_age.get_age(thing.posted)
    return render_template('view_paste.html', cur_paste=cur_paste, recent_pastes=recent_pastes, highlighted=highlighted, error=error)

@app.route('/view/all/')
def view_all_pastes():
    if 'logged_in' not in session.keys() or session['logged_in'] != True:
        abort(404)
    all_pastes = pastes.query.order_by(pastes.posted.desc()).limit(40).all()
    for paste in all_pastes:
        paste.posted = pretty_age.get_age(paste.posted)
    return render_template('paste_list.html', pastes=all_pastes)


@app.route('/unlisted/<int:paste_hash>/')
def view_unlisted_paste(paste_hash):
    error = None
    highlighted = None
    cur_paste = pastes.query.filter_by(p_hash=paste_hash).first()
    if cur_paste == None:
        abort(404)
    cur_paste.posted = pretty_age.get_age(cur_paste.posted)
    try: highlighted = highlight.syntax(cur_paste.contents, cur_paste.language)
    except:
        error = 'That language has no highlighting available! Oops! <a href="mailto://%(email)s">email</a> me and tell me to fix it!' % { 'email': app.config['EMAIL'] }
        highlighted = highlight.syntax(cur_paste.contents, 'none')
    recent_pastes = pastes.query.filter_by(unlisted=0).order_by(pastes.posted.desc()).limit(7).all()
    for thing in recent_pastes:
        thing.posted = pretty_age.get_age(thing.posted)
    return render_template('view_paste.html', cur_paste=cur_paste, recent_pastes=recent_pastes, highlighted=highlighted, error=error)

@app.route('/api/')
def api():
    return render_template('api.html')

# API

@app.route('/api/add', methods=['POST'])
def api_add():
    r = request
    if r.form['contents'] == '':
        return jsonify(success=False, error='No content')
    p_hash = str(random.getrandbits(50))[:7]
    p = addPaste(r.form['title'], r.form['contents'], None, r.form['language'].lower(), r.form['unlisted'], p_hash)
    if r.form['unlisted'] == '1':
        return jsonify(success=True, url=url_for('view_unlisted_paste', paste_hash=p.p_hash, _external=True))
    else:
        return jsonify(success=True, url=url_for('view_paste', paste_id=p.id, _external=True))


# Errors

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()