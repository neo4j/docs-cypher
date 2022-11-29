import pytest
import logging
import pprint

from textwrap import dedent
from prettytable import PrettyTable

log = logging.getLogger()
pp = pprint.PrettyPrinter(indent=1, width=120, sort_dicts=False)

# python -m pytest tests/test_query_plan_AllNodesScan.py
def test_consume(neo4j_container):

    test_id = "9c50f265-f7e9-4a9a-a4c2-871b02ae22e6"

    adoc_path = "docs-cypher/modules/ROOT/pages/clauses/match.adoc"

    # Test that the ID for the test is present on a specific page
    # Test that the example is present on a specific page

    example = dedent('''\
    MATCH (n)
    RETURN n''')

    # Test that the result is present on a specific page
    result = dedent('''\
    +------------------------------------------------+
    | n                                              |
    +------------------------------------------------+
    | Node(:Person {name: 'Charlie Sheen'})          |
    | Node(:Person {name: 'Martin Sheen'})           |
    | Node(:Person {name: 'Michael Douglas'})        |
    | Node(:Person {name: 'Oliver Stone'})           |
    | Node(:Person {name: 'Rob Reiner'})             |
    | Node(:Movie {title: 'Wall Street'})            |
    | Node(:Movie {title: 'The American President'}) |
    +------------------------------------------------+''')
    # neo4j.GraphDatabase.driver
    driver = neo4j_container.get_driver()

    # CLEAN
    with driver.session() as session:
        session.run("MATCH (_) DETACH DELETE _").consume()

    # STATE
    with driver.session() as session:
        q = dedent('''\
        CREATE
          (charlie:Person {name: 'Charlie Sheen', ix: 0}),
          (martin:Person {name: 'Martin Sheen', ix: 1}),
          (michael:Person {name: 'Michael Douglas', ix: 2}),
          (oliver:Person {name: 'Oliver Stone', ix: 3}),
          (rob:Person {name: 'Rob Reiner', ix: 4}),
          (wallStreet:Movie {title: 'Wall Street', ix: 5}),
          (charlie)-[:ACTED_IN {role: 'Bud Fox'}]->(wallStreet),
          (martin)-[:ACTED_IN {role: 'Carl Fox'}]->(wallStreet),
          (michael)-[:ACTED_IN {role: 'Gordon Gekko'}]->(wallStreet),
          (oliver)-[:DIRECTED]->(wallStreet),
          (thePresident:Movie {title: 'The American President', ix: 6}),
          (martin)-[:ACTED_IN {role: 'A.J. MacInerney'}]->(thePresident),
          (michael)-[:ACTED_IN {role: 'President Andrew Shepherd'}]->(thePresident),
          (rob)-[:DIRECTED]->(thePresident)''')

        _ = session.run(q).consume()

    # EXAMPLE
    def match_person_nodes(tx):
        q = dedent(example + " ORDER BY n.ix")
        result = tx.run(q)
        data = []   
        for record in result:
            if record["n"]["title"]:
                data.append(["Node(:" + list(record["n"].labels)[0] + " {title: '" + record["n"]["title"] + "'})"])
            elif record["n"]["name"]:
                data.append(["Node(:" + list(record["n"].labels)[0]  + " {name: '" + record["n"]["name"] + "'})"])
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

    assert keys == ["n"]

    pt = PrettyTable()
    pt.align = "l"

    pt.field_names = keys

    for row in data:
        pt.add_row(row)

    log.info("\n{}".format(pt))

    assert result == str(pt)

