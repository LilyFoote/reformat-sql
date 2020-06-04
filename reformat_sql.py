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
    row = []
    for token in sqlparse.parse(sql)[0].tokens:
        if isinstance(token, IdentifierList):
            row.extend(format_identifier_list(token))
        else:
            if token.is_keyword:
                indent = None
                if token.value in ('FROM', 'ON'):
                    indent = 8
                elif token.value in ('LIMIT', 'INNER JOIN', 'LEFT OUTER JOIN'):
                    indent = 4
                if indent is not None:
                    # trim trailing whitespace
                    output.append(''.join(row[:-1]))
                    row = [' ' * indent]
            row.append(str(token))

    output.append(''.join(row))
    # include trailing newline
    output.append('')
    return '\n'.join(output)
