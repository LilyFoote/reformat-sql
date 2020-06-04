import sqlparse
from sqlparse.sql import Identifier, IdentifierList, Parenthesis, Token, Where
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


def format_where_parentheses(parenthesis, indent):
    rows = []
    row = []
    for token in parenthesis.tokens:
        if isinstance(token, Parenthesis):
            first, rest = format_where_parentheses(token, indent + 4)
            row.extend(first)
            rows.append(row)
            rows.extend(rest)
            row = [' ' * indent]
        elif token.is_keyword:
            if row:
                rows.append(row[:-1])
            row = [' ' * indent, str(token)]
        else:
            row.append(str(token))
    if row:
        rows.append(row)

    return rows[0], rows[1:]


def format_where(where, indent=4):
    rows = []
    row = [' ' * indent]
    for token in where.tokens:
        if isinstance(token, Parenthesis):
            first, rest = format_where_parentheses(token, indent + 4)
            row.extend(first)
            rows.append(row)
            rows.extend(rest)
            row = []
        else:
            row.append(str(token))
    if row:
        rows.append(row)

    return rows


def format_sql(sql):
    output = []
    row = []
    for token in sqlparse.parse(sql)[0].tokens:
        if isinstance(token, IdentifierList):
            row.extend(format_identifier_list(token))
        elif isinstance(token, Where):
            output.append(''.join(row[:-1]))
            rows = format_where(token)
            for row in rows[:-1]:
                output.append(''.join(row))
            row = rows[-1]
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
