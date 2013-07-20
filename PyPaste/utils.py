from flask import url_for
from PyPaste import app


def create_paste_url(paste, relative=False):
    """
    Generates a url for the given paste.
    Paste should be a dict returned by
    Paste.by_id, etc

    """
    unlisted = paste['unlisted']
    if unlisted:
        return pypaste_url_for(
            'pastes.unlisted',
            paste_hash=paste['hash'],
            _external=not relative
        )
    else:
        return pypaste_url_for(
            'pastes.public',
            paste_id=paste['id'],
            _external=not relative
        )


def pypaste_url_for(endpoint, **kwargs):
    if (app.config.get('FORCE_SSL', False)
    or kwargs.get('_scheme', False) == 'https'):
        # Flask 0.10 supports the _scheme kwarg in url_for,
        # but 0.9 is the latest version on PyPi.

        if '_external' in kwargs:
            # Remove conflict
            del kwargs['_external']

        if '_scheme' in kwargs:
            del kwargs['_scheme']

        url = url_for(endpoint, _external=True, **kwargs)
        return 'https' + url[4:]
    else:
        return url_for(endpoint, **kwargs)
