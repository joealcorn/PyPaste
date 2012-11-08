from pygments import highlight
from pygments.lexers import *
from pygments.formatters import HtmlFormatter

formatter = HtmlFormatter(linenos=True, lineanchors='line', anchorlinenos=True)
languages = {
                'text': TextLexer(),
                'none': TextLexer(),
                'c': CLexer(),
                'cpp': CppLexer(),
                'csharp': CSharpLexer(),
                'css': CssLexer(),
                'erlang': ErlangLexer(),
                'go': GoLexer(),
                'html': HtmlLexer(),
                'java': JavaLexer(),
                'javascript': JavascriptLexer(),
                'json': JSONLexer(),
                'objectivec': ObjectiveCLexer(),
                'perl': PerlLexer(),
                'python': PythonLexer(),
                'python3': Python3Lexer(),
                'pytraceback': PythonTracebackLexer(),
                'ruby': RubyLexer(),
                'sql': SqlLexer(),
                'vbnet': VbNetLexer()
            }


def syntax(code, language):
    try:
        lang = languages[language]
    except KeyError:
        lang = languages['text']
    return highlight(code, lang, formatter)
