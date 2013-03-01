import bcrypt
import psycopg2
from psycopg2.extras import DictCursor

from PyPaste import config


class User(object):

    conn = psycopg2.connect(
        database=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
        host=config.PG_HOST,
        port=config.PG_PORT
    )

    @classmethod
    def _cursor(self):
        return self.conn.cursor(cursor_factory=DictCursor)

    @staticmethod
    def _hash_password(password, hashed=None):
        if hashed is None:
            # First time a pw has been hashed, gen a salt
            return bcrypt.hashpw(password, bcrypt.gensalt())
        else:
            return bcrypt.hashpw(password, hashed)

    @classmethod
    def init_table(self):
        cur = self._cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users
            (
                id serial PRIMARY KEY UNIQUE,
                username varchar(25) UNIQUE,
                password varchar(60),
                active boolean
            );
            """
        )
        self.conn.commit()
        cur.close()

    @classmethod
    def new(self):
        pass

    @classmethod
    def by_username(self, username):
        cur = self._cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        return user

    @classmethod
    def match_password(self, username, password):
        user = self.by_username(username)
        if user is None:
            return False

        current = user['password']
        if not self._hash_password(password, current) == current:
            # Incorrect password
            # Todo: track failed attempts
            return False
        return True
