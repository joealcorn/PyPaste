from flask.ext import wtf


class NewPaste(wtf.Form):
    text = wtf.TextAreaField('text', validators=[wtf.Required()])
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


class PastePassword(wtf.Form):
    paste_hash = wtf.TextField(validators=[wtf.Required()])
    redirect = wtf.TextField(validators=[wtf.Required()])
    password = wtf.PasswordField('password', validators=[wtf.Required()])
    submit = wtf.SubmitField('Submit')
