import logging
import pprint

from textwrap import dedent

log = logging.getLogger()
pp = pprint.PrettyPrinter(indent=1, width=120, sort_dicts=False)

# python -m pytest tests/test_execution_operators.py
def test_allNodesScan(neo4j_container, before_cleanup):
    #test_id = "8563b9dd-31ed-49fe-9c04-a491377526d0"

    #adoc = "/home/martin/WSPACEDOCS/docs-cypher/modules/ROOT/pages/execution-plans/operators.adoc"

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
        data = []   
        for record in result:
            data.append([record["n"]["ix"], record["n"]["name"]]) 
        summary = result.consume()
        return (result.keys(), data, summary)

    with driver.session() as session:
        keys, data, summary = session.read_transaction(match_person_nodes)

    driver.close()

    assert keys == ["n"]
    log.info(data)
    assert data == [[7, "Alice"],[2, "Bob"]]
    log.info('assert summary.profile[args][runtime] == PIPLINED \n')
    assert summary.profile['args']['runtime'] == 'PIPELINED'
    log.info('assert summary.profile[args][planner] == COST \n')
    assert summary.profile['args']['planner'] == 'COST'
    log.info('assert summary.profile[operatorType] got text ProduceResults \n')
    assert 'ProduceResults' in summary.profile['operatorType']
    log.info('assert summary.profile[children][operatorType] got text AllNodesScan \n')
    assert 'AllNodesScan' in summary.profile['children'][0]['operatorType']
