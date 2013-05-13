"""
Most commands in here are custom to my
local or server config, they'll need to
be adjusted if you wish to use them

"""

from getpass import getpass
import os
from glob import glob

from fabric.api import task, env, cd, run, local, prefix

from PyPaste.models.pastes import Paste
from PyPaste.models.users import User
from PyPaste.utils import create_paste_url

env.hosts = ['paste.buttscicl.es']


@task
def deploy(remote='origin', branch='master'):
    with cd('~/projects/PyPaste/'):
        run('git pull %s %s' % (remote, branch))
        with prefix('source ~/venvs/pypaste/bin/activate'):
            run('pip install -r requirements.txt')
        run('pkill -f --signal HUP "gunicorn: master \[PyPaste\]"')


@task
def test():
    os.environ['PYPASTE_TESTING'] = '1'
    local('nosetests -v')
    os.environ.pop('PYPASTE_TESTING')


@task
def highlight_examples():
    extensions = {
        'py': 'python',
        'json': 'json'
    }

    files = glob('/home/joe/git/PyPaste/PyPaste/views/api/v1/templates/examples/*')
    files = [f for f in files if not f.endswith('.html')]
    for f in files:
        extension = f.rsplit('.', 1)[1]
        local('{pygments} -f html -l {ext} -O {opt} -o {output} {input}'.format(
            pygments='/home/joe/.venvs/pypaste/bin/pygmentize',
            ext=extensions[extension],
            opt='linenos=1,lineanchors=line,anchorlinenos=1',
            input=f,
            output=f.replace('.' + extension, '.html')
        ))


@task
def add_user(username=None):
    if username is None:
        username = raw_input('Username: ')

    password = getpass('Password: ')
    if User.new(username, password):
        print 'Success.'
    else:
        print 'Failure, try again.'


@task
def shortlink_backfill():
    cur = Paste._cursor()
    cur.execute(
        """
        SELECT * from pastes
        WHERE shortlink is null
        """
    )
    pastes = cur.fetchall()

    for paste in pastes:
        if paste['unlisted']:
            url = 'https://paste.buttscicl.es/u/' + paste['hash']
        else:
            url = 'https://paste.buttscicl.es/p/' + str(paste['id'])

        shortlink = Paste.get_shortlink(url)
        if shortlink is not None:
            cur.execute(
                """
                UPDATE pastes SET shortlink = %s
                WHERE hash = %s
                """, (shortlink, paste['hash'])
            )
            Paste.conn.commit()
            print 'Done #' + str(paste['id'])

    cur.close()
