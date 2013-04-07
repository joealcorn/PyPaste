#!/usr/bin/env python

from getpass import getpass

from PyPaste.models.users import User

if __name__ == '__main__':
    username = raw_input('Username: ')
    password = getpass('Password: ')

    if User.new(username, password):
        print 'Success.'
    else:
        print 'Failure, try again.'
