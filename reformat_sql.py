import sqlparse
from sqlparse.sql import Identifier, IdentifierList, Token
from sqlparse.tokens import Wildcard


def format_identifier_list(identifier_list):
    first = identifier_list.token_first()
    first.tokens[-1] = Token(Wildcard, '*')
    current_name = first.get_parent_name()
    yield str(first)

    for token in identifier_list.tokens[1:]:
        if isinstance(token, Identifier):
            if token.get_parent_name() == current_name:
                continue

            token.tokens[-1] = Token(Wildcard, '*')
            current_name = token.get_parent_name()

            yield ',\n        '
            yield str(token)


def format_sql(sql):
    output = []
    for token in sqlparse.parse(sql)[0].tokens:
        if isinstance(token, IdentifierList):
            output.extend(format_identifier_list(token))
        else:
            if token.is_keyword:
                indent = None
                if token.value in ('FROM', 'ON'):
                    indent = 8
                elif token.value in ('LIMIT', 'INNER JOIN', 'LEFT OUTER JOIN'):
                    indent = 4
                if indent is not None:
                    output[-1] = '\n' + ' ' * indent
            output.append(str(token))

    output.append('\n')
    return ''.join(output)
