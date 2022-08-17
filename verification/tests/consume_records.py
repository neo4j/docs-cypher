import pytest
import logging

from textwrap import dedent
from prettytable import PrettyTable

log = logging.getLogger()

# python -m pytest tests/consume_records.py
def test_consume(neo4j_container):

    # neo4j.GraphDatabase.driver
    driver = neo4j_container.get_driver()

    # CLEAN
    with driver.session() as session:
        session.run("MATCH (_) DETACH DELETE _").consume()

    # STATE
    with driver.session() as session:
        session.run("CREATE (a:Person {name: $name, ix: $ix}) RETURN a", name="Alice", ix=7).single().value()
        session.run("CREATE (a:Person {name: $name, ix: $ix}) RETURN a", name="Bob", ix=2).single().value()

    # EXAMPLE
    def match_person_nodes(tx):
        q = dedent('''\
        MATCH (a:Person)
        RETURN
          a.ix AS repr,
          a.name AS name
        ORDER BY a.name''')
        result = tx.run(q)
        data = [[record["repr"], record["name"]] for record in result]
        return (result.keys(), data)

    with driver.session() as session:
        keys, data = session.read_transaction(match_person_nodes)

    driver.close()

    log.info(data)

    assert keys == ["repr", "name"]
    assert data == [
        [7, "Alice"],
        [2, "Bob"],
    ]

    pt = PrettyTable()
    pt.align = "l"

    pt.field_names = keys

    for row in data:
        # TODO: convert to representation for different types
        #
        # https://github.com/jazzband/prettytable#style-options
        # custom_format
        #
        # Integer: 0, 1, -2
        # Float:
        # NaN:
        # String: 'Example', 'ABCDEF'
        # Boolean: true, false
        # Null: null
        # Map:
        # List
        # Node:
        # Relationship:
        # Path:
        # Date:
        # Time:
        # LocalTime:
        # DateTime:
        # LocalDateTime:
        # Duration:
        # Point:
        pt.add_row(row)

    log.info("\n{}".format(pt))

    assert str(pt) == dedent('''\
    +------+-------+
    | repr | name  |
    +------+-------+
    | 7    | Alice |
    | 2    | Bob   |
    +------+-------+''')

    # Test that the ID for the test is present on a specific page
    # Test that the example is present on a specific page
    # Test that the result is present on a specific page

