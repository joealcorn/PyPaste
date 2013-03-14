from PyPaste.models import BaseModel


class User(BaseModel):

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
        pastes = self._by_param('username', username)
        return pastes

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
