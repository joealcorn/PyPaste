import json

from flask import session

from PyPaste import app
from PyPaste.models.pastes import Paste


class TestBase(object):

    def setUp(self):
        app.config['CSRF_ENABLED'] = False
        self.app = app.test_client()
        Paste.init_table()

    def tearDown(self):
        # drop the table so we can
        # recreate it for other tests
        cur = Paste._cursor()
        cur.execute('DROP TABLE pastes')
        cur.connection.commit()
        cur.close()


class test_legacy_api_compat(TestBase):

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
        data = json.loads(r.data)
        assert data['password'] == 'hunter2'

    def test_legacy_api_compat_3(self):
        r = self.legacy_api_post(title='failure')
        assert r.mimetype == 'application/json'

        data = json.loads(r.data)
        assert not data['success']
        assert isinstance(data['error'], list)

    def test_unlisted_paste(self):
        r = self.legacy_api_post(contents='1', unlisted=1)
        d = json.loads(r.data)
        assert '/u/' in d['url']

    def test_public_paste(self):
        r = self.legacy_api_post(contents='1', unlisted=0)
        d = json.loads(r.data)
        assert '/p/' in d['url']


class test_core_functionality(TestBase):

    def test_paste_creation(self):
        p = Paste.new("Look, we're testing!", password='hunter2')

        # Pasting succeeded
        assert p is not None
        assert p['id'] == 1

        # Check passwords are being hashed
        # bcrypt outputs 60 bytes
        assert p['password'] != 'hunter2'
        assert len(p['password']) == 60

        # Now check paste creation using the web
        r = self.app.post('/', data=dict(
            text='test',
            title='',
            password='',
            language='text',
            unlisted=None
        ))

        # Grab the newly made paste
        p = Paste.by_id(2)

        assert p['text'] == 'test'
        assert p['password'] is None
        assert r.status_code == 302

    def test_unlisted_paste(self):
        p = Paste.new('Test', unlisted=True)
        id = p['id']
        hash = p['hash']

        # Unlisted pastes should only be
        # accessed via /u/:hash
        r = self.app.get('/p/{0}/'.format(id))
        assert r.status_code == 404

        r = self.app.get('/u/{0}/'.format(hash))
        assert r.status_code == 200

    def test_password_protection(self):
        Paste.new('Test', password='hunter2')

        r = self.app.get('/p/1/')

        # 401 = unauthorised
        assert r.status_code == 401
        assert r.mimetype == 'text/html'

    def test_password_authentication(self):
        p = Paste.new('Test', password='hunter2')

        with app.test_client() as c:
            r = c.post('/p/authorise', data=dict(
                paste_hash=p['hash'],
                password='hunter2',
                redirect='http://localhost/p/1/',
            ))

            # Check we've got the correct cookie
            # and are being redirected
            assert p['hash'] in session.get('authorised_pastes')
            assert r.status_code == 302

    def test_raw_paste(self):
        Paste.new('Hello World!')
        r = self.app.get('/p/1/raw/')
        assert r.status_code == 200
        assert r.mimetype == 'text/plain'


class test_v1_api(TestBase):

    def new_paste(self, **kw):
        return self.app.post('/api/v1/new', data=kw)

    def test_api_creation(self):
        r = self.new_paste(text='Hello')
        assert r.status_code == 200

    def test_public_creation(self):
        r = self.new_paste(text='Hi')
        d = json.loads(r.data)
        assert '/p/' in d['url']

    def test_unlisted_creation(self):
        r = self.new_paste(text='Hi', unlisted='t')
        d = json.loads(r.data)
        assert '/u/' in d['url']

    def test_password_creation(self):
        r = self.new_paste(text='1', password='hunter2')
        d = json.loads(r.data)
        assert d['password'] == 'hunter2'

    def test_404_error(self):
        r = self.app.get('/api/v1/nonexistent')
        assert r.status_code == 404
        assert r.mimetype == 'application/json'

    def test_405_error(self):
        r = self.app.get('/api/v1/new')
        assert r.status_code == 405
        assert r.mimetype == 'application/json'
