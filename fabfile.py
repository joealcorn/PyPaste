from fabric.api import task

from PyPaste.models.pastes import Paste
from PyPaste.utils import create_paste_url


@task
def shortlink_backfill():
    cur = Paste._cursor()
    cur.execute(
        """
        SELECT * from pastes
        WHERE shortlink is null
        """
    )
    pastes = cur.fetchall()

    for paste in pastes:
        if paste['unlisted']:
            url = 'https://paste.buttscicl.es/u/' + paste['hash']
        else:
            url = 'https://paste.buttscicl.es/p/' + str(paste['id'])

        shortlink = Paste.get_shortlink(url)
        if shortlink is not None:
            cur.execute(
                """
                UPDATE pastes SET shortlink = %s
                WHERE hash = %s
                """, (shortlink, paste['hash'])
            )
            Paste.conn.commit()
            print 'Done #' + str(paste['id'])

    cur.close()
