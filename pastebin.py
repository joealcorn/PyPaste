from flask import Flask, redirect, url_for, render_template, flash, request, abort, jsonify
from flaskext.sqlalchemy import SQLAlchemy
from datetime import datetime
import highlight

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

class paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posted = db.Column(db.DateTime)
    title = db.Column(db.String(50))
    contents = db.Column(db.Text)
    password = db.Column(db.String(20))
    language = db.Column(db.String(40))
    
    def __init__(self, title, contents, password, language):
        self.posted = datetime.utcnow()
        self.title = title
        self.contents = contents
        self.password = password
        self.language = language

def addPaste(title, contents, password, language):
    if title == '':
        title = "Untitled"
    if contents == '':
        flash('You need to paste some text')
        return
    p = paste(title, contents, password, language)
    db.session.add(p)
    db.session.commit()

@app.route('/add/', methods=['POST', 'GET'])
def add():
    r = request
    if r.method == 'GET':
        return redirect(url_for('index'))        
    addPaste(r.form['title'], r.form['contents'], None, r.form['language'])
    return redirect(url_for('index'))

# Pages

@app.route('/')
def index():
    error = None
    pastes = paste.query.order_by(paste.posted.desc()).limit(7).all()
    for thing in pastes:
        if len(thing.title) >= 15:
            thing.title = thing.title[:12] + '...'
        thing.posted = datetime.utcnow() - thing.posted
        thing.posted = str(thing.posted).split('.')[0]
    return render_template('add_paste.html', pastes=pastes, error=error)

@app.route('/view/')
def view_list():
    error = None
    pastes = paste.query.order_by(paste.posted.desc()).limit(40).all()
    for thing in pastes:
        thing.title = thing.title[:50]
        thing.contents = thing.contents[:40]
        thing.posted = datetime.utcnow() - thing.posted
        thing.posted = str(thing.posted).split('.')[0]
    return render_template('paste_list.html', pastes=pastes, error=error)

@app.route('/view/<int:paste_id>/')
def view_paste(paste_id):
    error = None
    highlighted = None
    cur_paste = paste.query.get(paste_id)
    if cur_paste == None:
        abort(404)
    title = cur_paste.title
    try: highlighted = highlight.syntax(cur_paste.contents, cur_paste.language)
    except:
        ''' In the case where the user was able to select a language which has no syntax highlighting configured 
            (by sending a POST request and not using the form) it will alert them to it '''
        error = 'That language has no highlighting available! Oops! <a href="mailto://%(email)s">email</a> me and tell me to fix it!' % { 'email': app.config['EMAIL'] }    
        highlighted = highlight.syntax(cur_paste.contents, 'none')
    recent_pastes = paste.query.order_by(paste.posted.desc()).limit(7).all()
    for thing in recent_pastes:
        if len(thing.title) >= 15:
            thing.title = thing.title[:12] + '...'
        thing.posted = datetime.utcnow() - thing.posted
        thing.posted = str(thing.posted).split('.')[0]
    return render_template('view_paste.html', cur_paste=cur_paste, recent_pastes=recent_pastes, highlighted=highlighted, title=title, error=error)

# API

@app.route('/api/add', methods=['POST'])
def api_add():
    r = request
    try: addPaste(r.form['title'], r.form['contents'], None, r.form['language'])
    except: return jsonify(success=False)
    pastes = paste.query.order_by(paste.posted.desc()).limit(1).all()
     
    return jsonify(success=True, url=(url_for('view_list')+str(pastes[0].id)))

# Errors

@app.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
