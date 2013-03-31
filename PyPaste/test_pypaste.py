import json

import psycopg2

import PyPaste
from PyPaste.models.pastes import Paste

# This allows us to test
# against a seperate db
PyPaste.app.config['PG_DB'] = 'pypastetesting'

Paste.conn = psycopg2.connect(
    database=PyPaste.app.config['PG_DB'],
    user=PyPaste.app.config['PG_USER'],
    password=PyPaste.app.config['PG_PASSWORD'],
    host=PyPaste.app.config['PG_HOST'],
    port=PyPaste.app.config['PG_PORT']
)


class testCase:

    def setUp(self):
        self.app = PyPaste.app.test_client()
        Paste.init_table()

    def tearDown(self):
        # drop the table so we can
        # recreate it for other tests
        cur = Paste._cursor()
        cur.execute('DROP TABLE pastes')
        cur.connection.commit()
        cur.close()

    def legacy_api_post(self, **kw):
        return self.app.post('/api/add', data=kw)

    def legacy_api_assertions_success(self, response):
        assert response.status_code == 200
        assert response.mimetype == 'application/json'

        data = json.loads(response.data)
        assert data['success']

        # Check we're not returning relative URLs
        assert data['url'].startswith('http')

    def test_legacy_api_compat_1(self):
        r = self.legacy_api_post(
            contents='This is the only required field'
        )
        self.legacy_api_assertions_success(r)

    def test_legacy_api_compat_2(self):
        r = self.legacy_api_post(
            contents='example data',
            title='testing',
            password='hunter2',
            language='text',
            unlisted=0
        )
        self.legacy_api_assertions_success(r)

    def test_legacy_api_compat_3(self):
        r = self.legacy_api_post(title='failure')
        assert r.mimetype == 'application/json'

        data = json.loads(r.data)

        assert not data['success']
        assert isinstance(data['error'], list)
