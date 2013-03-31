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
        """
        Convenience method to grab a user by username

        """
        user = self._by_param('username', username, table='users')
        return user

    @classmethod
    def password_match(self, username, password):
        """
        Checks if $password is the correct password for $username
        """
        return self._password_match(username, password, _type='user')
