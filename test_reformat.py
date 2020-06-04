from textwrap import dedent

from reformat_sql import format_sql


def test_format_sql():
    sql = 'SELECT "library_author"."id", "library_author"."name", "library_author"."date_of_birth", "library_author"."biography" FROM "library_author" LIMIT 21'

    expected_sql = dedent('''\
    SELECT "library_author".*
            FROM "library_author"
        LIMIT 21
    ''')

    assert format_sql(sql) == expected_sql
