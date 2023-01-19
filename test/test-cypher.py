from functions import *
import neo4j
from glob import glob
import pytest
import os


"""
TO DO
- handle result types: Path, dict
"""


path = os.getenv('CYPHER_TEST_PATH', 'modules/ROOT/**/*.adoc').split(',')
filenames = []
for filename in path:
    filenames += glob(filename.strip(), recursive=True)
print(f'Testing the following files: {filenames}.')


@pytest.mark.parametrize('filename', filenames)  # each file spawns a TestClass
class TestClass:
    def test_file(self, subtests, filename):
        self.filename = filename
        self.driver = get_driver()
        clean_database(self.driver)
        asciidoc = open(self.filename).read()
        if r':test-skip: true' in asciidoc:
            pytest.skip(f'Honoring :test-skip: directive in {filename}.')
        examples = extract_examples_from_asciidoc(asciidoc)
        print(f'Found {len(examples)} examples in {self.filename}.')
        for example in examples:
            with subtests.test():
                self.run_example(**example)  # unwrap dict item
        self.driver.close()

    def run_example(self, tag, query, docs_result):
        print(f'\n== File `{self.filename}`')
        print(f'== Tag `{tag}`')
        print(f'== Testing `{query}`')
        print(f'== Docs result:\n{docs_result}')

        self.maybe_skip(tag, query)

        # Allow semicolon to split statements.
        # Don't abuse of it, only use it for setup blocks.
        # If one setup query fails, the ones after are ignored (because of assert in except).
        for query in query.split(';'):
            if query == '':  # empty lines, or semicolon after last statement
                continue

            with self.driver.session(database='neo4j') as session:
                try:
                    result = session.run(query)
                    records = list(result)
                except Exception as exception:
                    assert 'test-fail' in tag, f"Query failed, but it's not marked as test-fail in docs.\n{query}\n{exception}"
                    continue

                if docs_result == None:  # no result to compare against, test ends here
                    continue

                # Query was successful and there is a result to compare against -> validate result
                if 'PROFILE' in query:
                    # profile queries are tested by comparing operators list
                    query_plan = result.consume().profile['args']['string-representation']
                    assert extract_plan_operators(docs_result) == extract_plan_operators(query_plan)
                else:
                    for record in records:
                        for (record_key, record_value) in record.items():
                            self.validate_result(query, record_key, record_value, docs_result)

    def maybe_skip(self, tag, query):
        exclude_functions = ['date()', 'datetime()', 'localdatetime()', 'localtime()', 'time()', 'timestamp()', 'randomUUID()', 'elementId(']

        if 'test-skip' in tag:
            pytest.skip(f'Example with role=test-skip\n{self.filename}\n{query}')
        if '$' in query:
            pytest.skip(f'Example with query parameters\n{self.filename}\n{query}')
        for function in exclude_functions:
            if function in query:
                pytest.skip(f'Example with {function}\n{self.filename}\n{query}')
        if 'LOAD' in query and '.csv' in query:
            pytest.skip(f'Example with csv loading\n{self.filename}\n{query}')

    # Test result by checking whether all properties values are found in docs result, somewhere.
    # For relationship, also check that relationship type is found.
    def validate_result(self, query, record_key, record_value, docs_result):
        if isinstance(record_value, neo4j.graph.Node):
            self.is_node_in_result(record_value, docs_result)
        elif isinstance(record_value, neo4j.graph.Relationship):
            self.is_relationship_in_result(record_value, docs_result)
        elif isinstance(record_value, neo4j.graph.Path):
            pytest.skip(f'Example with path result\n{self.filename}\n{query}')
        elif isinstance(record_value, (str, int, bool)):
            self.is_property_in_result(record_key, record_value, docs_result)
        elif isinstance(record_value, list):
            for element in record_value:
                self.validate_result(query, record_key, element, docs_result)
        elif record_value != None:  # allow results where only _some_ fields are null
            pytest.skip(f'Example with result of unhandlable type {type(record_value)} \n{self.filename}\n{query}')

    def is_node_in_result(self, node, docs_result):
        for (key, value) in node.items():
            self.is_property_in_result(key, value, docs_result)

    def is_relationship_in_result(self, relationship, docs_result):
        assert relationship.type in docs_result
        for (key, value) in relationship.items():
            self.is_property_in_result(key, value, docs_result)

    def is_property_in_result(self, key, value, docs_result):
        assert str(value).lower() in docs_result.lower()
