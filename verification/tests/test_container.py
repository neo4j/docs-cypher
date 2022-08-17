import pytest
import logging

from textwrap import dedent

from neo4j.graph import (
    Node,
    Path,
    Relationship,
)

log = logging.getLogger()

# python -m pytest tests/test_container.py
def test_cypher(neo4j_container):
    log.info("running test")

    # https://github.com/testcontainers/testcontainers-python/blob/master/testcontainers/neo4j.py#L84
    # neo4j.GraphDatabase.driver
    driver = neo4j_container.get_driver()

    # CLEAN
    with driver.session() as session:
        q = dedent('''\
        MATCH (n)
        DETACH DELETE n''')
        result = session.run(q)
        record = result.consume()

    # STATE
    with driver.session() as session:
        q = dedent('''\
        CREATE
          (n1:Example {age: 55, happy: 'Yes!', name: 'A'}),
          (n2:Example:Person {name: 'B'}),
          (n1)-[r1:BLOCKS]->(n2),
          (n1)-[r2:KNOWS]->(n2)''')
        result = session.run(q)
        record = result.consume()

    # TEST
    with driver.session() as session:
        result = session.run("MATCH (n {name: 'B'}) RETURN n")
        record = result.single()
        log.info(record)
        assert result.keys() == ["n"]
        assert record is not None
        assert isinstance(record["n"], Node)

    driver.close()

