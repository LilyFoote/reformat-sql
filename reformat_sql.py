import sqlparse
from sqlparse.sql import (
    Case, Identifier, IdentifierList, Parenthesis, Token, Where
)
from sqlparse.tokens import Wildcard


def format_case(token, indent=8):
    rows = []
    row = [' ' * indent]

    case, *rest = token.tokens
    for part in case.tokens:
        if part.is_keyword:
            if part.value in ('WHEN', 'ELSE'):
                rows.append(row[:-1])
                row = [' ' * (indent + 4)]
            elif part.value == 'THEN':
                rows.append(row[:-1])
                row = [' ' * (indent + 8)]
            elif part.value == 'END':
                rows.append(row[:-1])
                row = [' ' * indent]

        row.append(str(part))

    for part in rest:
        row.append(str(part))

    if row:
        rows.append(row)
    return rows


def format_order_by(identifier_list, row, indent=8):
    rows = []
    first = identifier_list.token_first()
    row.append(str(first))
    for token in identifier_list[1:]:
        if isinstance(token, Identifier):
            row.append(',')
            rows.append(row)
            row = [' ' * indent, str(token)]

    rows.append(row)
    return rows


def format_identifier_list(identifier_list, row):
    first = identifier_list.token_first()
    if first.tokens[-1].is_keyword:
        return format_order_by(identifier_list, row)

    first.tokens[-1] = Token(Wildcard, '*')
    current_name = first.get_parent_name()
    row.append(str(first))
    rows = []

    for token in identifier_list.tokens[1:]:
        if isinstance(token, Identifier):
            if token.get_parent_name() == current_name:
                continue

            if not token.has_alias():
                token.tokens[-1] = Token(Wildcard, '*')
                current_name = token.get_parent_name()

            row.append(',')
            rows.append(row)

            if isinstance(token.token_first(), Case):
                case_rows = format_case(token)
                rows.extend(case_rows[:-1])
                row = case_rows[-1]
            else:
                row = [' ' * 8, str(token)]
    rows.append(row)
    return rows


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
            if ''.join(row).strip():
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


def format_token(token, row):
    rows = []
    if token.is_keyword:
        indent = None
        if token.value in ('FROM', 'ON'):
            indent = 8
        elif token.value in ('LIMIT', 'INNER JOIN', 'LEFT OUTER JOIN', 'ORDER BY'):
            indent = 4
        if indent is not None:
            # trim trailing whitespace
            rows.append(''.join(row[:-1]))
            row = [' ' * indent]
    row.append(str(token))
    rows.append(row)
    return rows


def format_sql(sql):
    output = []
    row = []
    for token in sqlparse.parse(sql)[0].tokens:
        if isinstance(token, IdentifierList):
            rows = format_identifier_list(token, row)
        elif isinstance(token, Where):
            output.append(''.join(row[:-1]))
            rows = format_where(token)
        else:
            rows = format_token(token, row)
        for row in rows[:-1]:
            output.append(''.join(row))
        row = rows[-1]

    output.append(''.join(row))
    # include trailing newline
    output.append('')
    return '\n'.join(output)
