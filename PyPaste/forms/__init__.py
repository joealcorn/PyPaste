from flask.ext import wtf


class NewPaste(wtf.Form):
    text = wtf.TextField('uid') # honeypot field
    paste = wtf.TextAreaField('text', validators=[wtf.Required()])
    title = wtf.TextField('title', validators=[wtf.Optional()])
    password = wtf.PasswordField('password', validators=[wtf.Optional()])
    unlisted = wtf.BooleanField('Unlisted')
    submit = wtf.SubmitField('Paste')
    language = wtf.SelectField(
        'language',
        choices=[
            ('', ''),
            ('text', 'Text'),
            ('c', 'C'),
            ('csharp', 'C#'),
            ('cpp', 'C++'),
            ('css', 'CSS'),
            ('erlang', 'Erlang'),
            ('go', 'GO'),
            ('html', 'HTML'),
            ('java', 'Java'),
            ('javascript', 'Javascript'),
            ('json', 'JSON'),
            ('objectivec', 'Objective-C'),
            ('perl', 'Perl'),
            ('python', 'Python (2.X)'),
            ('python3', 'Python (3.X)'),
            ('pycon', 'Python Console'),
            ('pytb', 'Python 2 Traceback'),
            ('py3tb', 'Python 3 Traceback'),
            ('ruby', 'Ruby'),
            ('sql', 'SQL'),
            ('vbnet', 'VB.NET'),
        ]
    )

    def validate_uid(form, field):
        """
        This ensures the hidden honeypot field is left blank,
        only automated spambots should attempt to fill it in
        """
        if field.data != '':
            raise wtf.validators.ValidationError()


class PastePassword(wtf.Form):
    paste_hash = wtf.TextField(validators=[wtf.Required()])
    redirect = wtf.TextField(validators=[wtf.Required()])
    password = wtf.PasswordField('password', validators=[wtf.Required()])
    submit = wtf.SubmitField('Submit')


class LoginForm(wtf.Form):
    username = wtf.TextField(validators=[wtf.Required()])
    password = wtf.PasswordField(validators=[wtf.Required()])
    submit = wtf.SubmitField('Login')


class LogoutForm(wtf.Form):
    username = wtf.TextField(validators=[wtf.Required()])
    submit = wtf.SubmitField('Confirm')


class DeletePasteForm(wtf.Form):
    paste_hash = wtf.html5.TextField(validators=[wtf.Required()])
    submit = wtf.SubmitField('Confirm')
