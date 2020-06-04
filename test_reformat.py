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


def test_format_joins():
    sql = 'SELECT "library_book"."id", "library_book"."name", "library_book"."author_id", "library_book"."publisher_id", "library_book"."synopsis", "library_book"."publish_date", "library_book"."edition", "library_author"."id", "library_author"."name", "library_author"."date_of_birth", "library_author"."biography", "library_publisher"."id", "library_publisher"."name" FROM "library_book" INNER JOIN "library_author" ON ("library_book"."author_id" = "library_author"."id") LEFT OUTER JOIN "library_publisher" ON ("library_book"."publisher_id" = "library_publisher"."id")'

    expected_sql = dedent('''\
    SELECT "library_book".*,
            "library_author".*,
            "library_publisher".*
            FROM "library_book"
        INNER JOIN "library_author"
            ON ("library_book"."author_id" = "library_author"."id")
        LEFT OUTER JOIN "library_publisher"
            ON ("library_book"."publisher_id" = "library_publisher"."id")
    ''')

    assert format_sql(sql) == expected_sql


def test_format_where():
    sql = r"""SELECT "library_book"."id", "library_book"."name", "library_book"."author_id", "library_book"."publisher_id", "library_book"."synopsis", "library_book"."publish_date", "library_book"."edition" FROM "library_book" WHERE "library_book"."name" LIKE '%tusk love%' ESCAPE '\'"""

    expected_sql = dedent('''\
    SELECT "library_book".*
            FROM "library_book"
        WHERE "library_book"."name" LIKE '%tusk love%' ESCAPE '\\'
    ''')

    assert format_sql(sql) == expected_sql
