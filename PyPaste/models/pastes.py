import psycopg2
from psycopg2.extras import DictCursor

from PyPaste import config


class Paste(object):

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

    @classmethod
    def _by_param(self, param, value):
        cur = self._cursor()
        cur.execute('SELECT * FROM pastes WHERE %s = %s', (param, value))
        return cur

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
    def new(self):
        pass

    @classmethod
    def by_id(self, _id):
        cur = self._by_param('id', _id)
        pastes = cur.fetchone()
        cur.close()
        return pastes

    @classmethod
    def by_hash(self, _hash):
        cur = self._by_param('hash', _hash)
        pastes = cur.fetchone()
        cur.close()
        return pastes
