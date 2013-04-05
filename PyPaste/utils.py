from flask import url_for


def create_paste_url(paste, relative=False):
    """
    Generates a url for the given paste.
    Paste should be a dict returned by
    Paste.by_id, etc

    """
    unlisted = paste['unlisted']
    if unlisted:
        return url_for(
            'pastes.unlisted',
            paste_hash=paste['hash'],
            _external=not relative
        )
    else:
        return url_for(
            'pastes.public',
            paste_id=paste['id'],
            _external=not relative
        )
