PyPaste
==========

Simple pastebin using Flask, Flask-SQLAlchemy and Pygments


Dependencies
===

Flask

Flask-SQLAlchemy

Pygments


Creating the database
===

To create the initial database, run:

```python
from pastebin import db
db.create_all()
```

