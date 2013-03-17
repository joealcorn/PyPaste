from os import urandom
from datetime import datetime
from hashlib import sha256, md5
from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto import Random
import psycopg2
from pygments import highlight, util
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

from PyPaste.models import BaseModel


class Paste(BaseModel):

    @staticmethod
    def _encrypt(key, plaintext):
        if isinstance(plaintext, unicode):
            # Convert to ascii
            plaintext = plaintext.encode('utf8')

        iv = Random.new().read(AES.block_size)
        key = sha256(key).digest()
        cipher = AES.new(key, AES.MODE_CFB, iv)
        ciphertext = iv + cipher.encrypt(plaintext)

        # b64 and back to unicode for storage
        ciphertext = b64encode(ciphertext)
        ciphertext = ciphertext.decode('utf8')
        return ciphertext

    @staticmethod
    def _decrypt(key, ciphertext):
        # Decode b64, also converts to str
        # Later converted back to unicode
        ciphertext = b64decode(ciphertext)

        key = sha256(key).digest()
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CFB, iv)
        plaintext = cipher.decrypt(ciphertext)[AES.block_size:]
        plaintext = plaintext.decode('utf8')

        return plaintext

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
        if isinstance(password, unicode):
            password = password.encode('utf8')

        if title is None:
            title = 'Untitled'

        (highlighted, language) = self._highlight(text, language)

        if unlisted not in (True, False):
            unlisted = False

        if password is not None:
            # Encrypt input text and hash password
            # Plaintext password is used as the key,
            # and bcrypt hash is stored
            text = self._encrypt(password, text)
            highlighted = self._encrypt(password, highlighted)
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
        pastes = self._by_param('id', _id)
        return pastes

    @classmethod
    def by_hash(self, _hash):
        pastes = self._by_param('hash', _hash)
        return pastes
