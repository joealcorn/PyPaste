from os import urandom
from datetime import datetime
from hashlib import md5

import psycopg2
from pygments import highlight, util
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

from PyPaste.models import BaseModel


class Paste(BaseModel):

    @staticmethod
    def _highlight(text, language='text'):
        if language is not None:
            try:
                lexer = get_lexer_by_name(language)
            except util.ClassNotFound:
                lexer = TextLexer()
        else:
            lexer = TextLexer()

        formatter = HtmlFormatter(
            linenos=True, lineanchors='line', anchorlinenos=True
        )
        return (highlight(text, lexer, formatter), lexer.name)

    @classmethod
    def init_table(self):
        cur = self._cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pastes
            (
                id serial PRIMARY KEY UNIQUE,
                hash varchar(32) UNIQUE,
                created timestamp,
                title varchar(50),
                text text,
                highlighted text,
                language varchar(20),
                password varchar(60),
                unlisted boolean
            );
            """
        )
        self.conn.commit()
        cur.close()

    @classmethod
    def new(self, text, title=None, language='text', password=None, unlisted=False):
        """
        Insert a new paste into the database.
        Returns the paste as a dict if successful.

        """
        if title is None:
            title = 'Untitled'

        (highlighted, language) = self._highlight(text, language)

        if unlisted not in (True, False):
            unlisted = False

        if password is not None:
            password = self._hash_password(password)

        _hash = md5(urandom(64)).hexdigest()

        cur = self._cursor()
        try:
            cur.execute(
                """
                INSERT INTO pastes
                (hash, created, title, text, highlighted, language,
                password, unlisted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (_hash, datetime.utcnow(), title, text, highlighted, language,
                password, unlisted)
            )
            self.conn.commit()
        except psycopg2.Error as e:
            print e
            self.conn.rollback()
            cur.close()
            return None

        cur.close()
        p = self.by_hash(_hash)
        return p

    @classmethod
    def by_id(self, _id):
        """
        Convenience method to grab a paste by ID

        """
        pastes = self._by_param('id', _id)
        return pastes

    @classmethod
    def by_hash(self, _hash):
        """
        Convenience method to grab a paste by hash

        """
        pastes = self._by_param('hash', _hash)
        return pastes

    @classmethod
    def password_match(self, paste_hash, password):
        """
        Checks if $password is the correct password for $paste_hash
        """
        return self._password_match(paste_hash, password)
