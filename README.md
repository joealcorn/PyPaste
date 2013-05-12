# PyPaste [![Build Status](https://travis-ci.org/buttscicles/PyPaste.png)](https://travis-ci.org/buttscicles/PyPaste)

Simple Python pastebin using Flask, Pygments & Postgres.


    $ git clone git://github.com/buttscicles/PyPaste.git
    $ cd PyPaste
    $ pip install -r requirements.txt
    $ cp PyPaste/config.py.default PyPaste/config.py
    $ python run.py

PyPaste implements a basic login system to allow admins to easily delete pastes, etc.  
`$ fab add_user` can be used to add users.

PyPaste has some test coverage, they can be run using a fab command
    
    $ fab test
