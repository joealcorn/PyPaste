import bcrypt
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import register_type, UNICODE

from PyPaste import config


class BaseModel(object):
    """
    Base class for both models providing
    some useful shared methods
    """

    conn = psycopg2.connect(
        database=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
        host=config.PG_HOST,
        port=config.PG_PORT
    )

    @classmethod
    def _cursor(self):
        """
        Returns a psycopg2 DictCursor

        """
        cur = self.conn.cursor(cursor_factory=DictCursor)
        register_type(UNICODE, cur)
        return cur

    @classmethod
    def _by_param(self, param, value, table='pastes', fetch_all=False):
        """
        Executes SQL query equivalent to
        'SELECT * FROM $table WHERE $param = $value'

        Only trusted input should be used for $table and $param

        """
        cur = self._cursor()
        # Although we should never use string
        # formatting techniques on sql strings,
        # it's OK here because only $value is
        # untrusted
        cur.execute(
            'SELECT * FROM {0} WHERE {1} = %s'.format(table, param),
            (value,)
        )
        if fetch_all:
            result = cur.fetchall()
        else:
            result = cur.fetchone()

        cur.close()
        return result

    @staticmethod
    def _hash_password(password, hashed=None):
        if hashed is None:
            # First time a pw has been hashed, gen a salt
            return bcrypt.hashpw(password, bcrypt.gensalt())
        else:
            return bcrypt.hashpw(password, hashed)
