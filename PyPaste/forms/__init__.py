from flask.ext import wtf


class NewPaste(wtf.Form):
    text = wtf.TextAreaField('text', validators=[wtf.Required()])
    title = wtf.TextField('title', validators=[wtf.Optional()])
    password = wtf.TextField('password', validators=[wtf.Optional()])
    unlisted = wtf.BooleanField('Unlisted')
    submit = wtf.SubmitField('Paste')
    language = wtf.SelectField(
        'language',
        choices=[
            ('', ''),
            ('auto', 'Automatic'),
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
            ('pytraceback', 'Python Traceback'),
            ('ruby', 'Ruby'),
            ('sql', 'SQL'),
            ('vbnet', 'VB.NET'),
        ]
    )
