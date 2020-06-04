import sqlparse
from sqlparse.sql import IdentifierList, Token
from sqlparse.tokens import Wildcard


def format_sql(sql):
    output = []
    for token in sqlparse.parse(sql)[0].tokens:
        if isinstance(token, IdentifierList):
            first = token.token_first()
            first.tokens[-1] = Token(Wildcard, '*')
            output.append(str(first))
        else:
            if token.is_keyword:
                if token.value == 'FROM':
                    output[-1] = '\n        '
                elif token.value == 'LIMIT':
                    output[-1] = '\n    '
            output.append(str(token))

    output.append('\n')
    return ''.join(output)
