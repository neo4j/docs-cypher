from functions import clean_state, extract_examples_from_asciidoc
from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship, Path
from pathlib import Path
import pytest

"""
TO DO
- command line argument for adoc files
- command line argument to specify docker image?
- clean_state should clear everything, including indexes, alias, etc
- make it runnable on a directory instead of a file
- make it runnable on a list of files
"""

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secret")
driver = GraphDatabase.driver(URI, auth=AUTH)
clean_state(driver)

#all_files = Path('.').glob('**/*.adoc')
filename = '../modules/ROOT/pages/clauses/where.adoc'
asciidoc = open(filename).read()
examples = extract_examples_from_asciidoc(asciidoc)

@pytest.mark.parametrize(
    "tag,query,docs_result", examples
)
def test_example(tag, query, docs_result):
    print(f'\n== Tag `{tag}`')
    print(f'== Testing `{query}`')
    print(f'Docs result:\n{docs_result}')

    if 'test-skip' in tag:
        pytest.skip(f'Example with role=test-skip\n{filename}\n{query}')
    if '$' in query:
        pytest.skip(f'Example with query parameters\n{filename}\n{query}')
    if '.csv' in query:
        pytest.skip(f'Example with csv loading\n{filename}\n{query}')
    if 'elementId(' in query:
        pytest.skip(f'Example with elementId\n{filename}\n{query}')
    
    with driver.session(database='neo4j') as session:
        try:
            result = session.run(query)
        except Exception:
            assert 'test-fail' in tag, "Query raised exception, but it's not marked as test-fail in docs"
            return
                
        records = list(result)
        for record in records:
            for (record_key, record_value) in record.items():
                if isinstance(record_value, Node):
                    assert is_node_in_result(record_value, docs_result)
                elif isinstance(record_value, Relationship):
                    assert is_relationship_in_result(record_value, docs_result)
                elif isinstance(record_value, Path):
                    pytest.skip(f'Example with path result\n{filename}\n{query}')
                elif isinstance(record_value, str):
                    assert is_property_in_result((record_key, record_value), docs_result)
                elif record_value == None:  # for results where only _some_ fields are null
                    continue
                else:
                    pytest.skip(f'Example with result of unhandlable type {type(record_value)} \n{filename}\n{query}')
    

def is_node_in_result(node, docs_result):
    for (key, value) in node.items():
        if value not in docs_result:
            return False
    return True
    
def is_relationship_in_result(relationship, docs_result):
    return is_node_in_result(relationship, docs_result)
    
def is_property_in_result(prop, docs_result):
    return prop[1] in docs_result


driver.close()
