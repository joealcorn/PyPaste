from pygments import highlight
from pygments.lexers import *
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, guess_lexer_for_filename

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
                'objectivec': ObjectiveCLexer(),
                'perl': PerlLexer(),
                'python': PythonLexer(),
                'python3': Python3Lexer(),
                'ruby': RubyLexer(),
                'sql': SqlLexer(),
                'vbnet': VbNetLexer()
            }
def syntax(code, language):
    lang = languages[language]
    return highlight(code, lang, formatter)

