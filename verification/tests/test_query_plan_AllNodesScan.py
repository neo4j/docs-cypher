import logging
import pprint

from textwrap import dedent
from prettytable import PrettyTable

log = logging.getLogger()
pp = pprint.PrettyPrinter(indent=1, width=120, sort_dicts=False)

# python -m pytest tests/test_query_plan_AllNodesScan.py
def test_allNodesScan(neo4j_container, before_cleanup):
    test_id = "8563b9dd-31ed-49fe-9c04-a491377526d0"

    adoc = "/home/martin/WSPACEDOCS/docs-cypher/modules/ROOT/pages/execution-plans/operators.adoc"

    # neo4j.GraphDatabase.driver
    driver = neo4j_container.get_driver()

    # STATE
    with driver.session() as session:
        session.run("CREATE (a:Person {name: $name, ix: $ix}) RETURN a", name="Alice", ix=7).single().value()
        session.run("CREATE (a:Person {name: $name, ix: $ix}) RETURN a", name="Bob", ix=2).single().value()

    # EXAMPLE
    def match_person_nodes(tx):
        q = dedent('''\
        PROFILE
        MATCH (n)
        RETURN n''')
        result = tx.run(q)
        data = [[record["n"],] for record in result]
        summary = result.consume()
        return (result.keys(), data, summary)

    with driver.session() as session:
        keys, data, summary = session.read_transaction(match_person_nodes)

    driver.close()

    log.info(data)
    log.info("\nCounters:\n{}".format(summary.counters))
    log.info("\nNotifications:\n{}".format(summary.notifications))
    log.info("\nQuery Plan:\n{}".format(summary.plan))
    profile = pp.pformat(summary.profile)
    log.info("\nQuery Profile:\n{}".format(profile))

    # assert keys == ["repr", "name"]
    # assert data == [
    #     [7, "Alice"],
    #     [2, "Bob"],
    # ]

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

    # Test that the ID for the test is present on a specific page
    # Test that the example is present on a specific page
    # Test that the result is present on a specific page

    # WSPACEDOCS/docs-cypher/modules/ROOT/pages/execution-plans/operators.adoc

