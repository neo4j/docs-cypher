from functions import *
import neo4j
from pathlib import Path
import pytest


"""
TO DO
- command line argument for running on a list of files
- command line argument for running on a directory
- command line argument to specify docker image?
- take neo4j credentials from ENV variables?
- clean_database should clear everything, including indexes, alias, etc
- handle result types: Path
"""


filenames = Path('../').glob('**/clauses/match.adoc')


@pytest.mark.parametrize('filename', filenames)  # each file spawns a TestClass
class TestClass:
    def test_file(self, subtests, filename):
        self.filename = filename
        self.driver = get_driver()
        clean_database(self.driver)
        asciidoc = open(self.filename).read()
        examples = extract_examples_from_asciidoc(asciidoc)
        print(f'Found {len(examples)} examples in {self.filename}.')
        for example in examples:
            with subtests.test():
                self.run_example(**example)  # unwrap dict item
        self.driver.close()

    def run_example(self, tag, query, docs_result):
        print(f'\n== Tag `{tag}`')
        print(f'== Testing `{query}`')
        print(f'== Docs result:\n{docs_result}')

        if 'test-skip' in tag:
            pytest.skip(f'Example with role=test-skip\n{self.filename}\n{query}')
        if '$' in query:
            pytest.skip(f'Example with query parameters\n{self.filename}\n{query}')
        if '.csv' in query:
            pytest.skip(f'Example with csv loading\n{self.filename}\n{query}')
        if 'elementId(' in query:
            pytest.skip(f'Example with elementId\n{self.filename}\n{query}')

        with self.driver.session(database='neo4j') as session:
            try:
                result = session.run(query)
            except Exception as exception:
                assert 'test-fail' in tag, f"Query raised exception, but it's not marked as test-fail in docs\n{exception}"
                return False

            if docs_result == None:  # no result to compare against, test ends here
                return True

            if 'PROFILE' in query:
                # profile queries are tested by comparing operators list
                query_plan = result.consume().profile['args']['string-representation']
                assert extract_plan_operators(docs_result) == extract_plan_operators(query_plan)
                return

            # Query was successful and there is a result to compare against -> validate result
            records = list(result)
            for record in records:
                print(record)
                for (record_key, record_value) in record.items():
                    self.validate_result(query, record_key, record_value, docs_result)

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
            self.is_property_in_result(record_key, str(record_value).lower(), docs_result.lower())
        elif isinstance(record_value, list):
            for element in record_value:
                self.validate_result(query, record_key, element, docs_result)
        elif record_value != None:  # allow results where only _some_ fields are null
            pytest.skip(f'Example with result of unhandlable type {type(record_value)} \n{self.filename}\n{query}')

    def is_node_in_result(self, node, docs_result):
        for (key, value) in node.items():
            assert value in docs_result

    def is_relationship_in_result(self, relationship, docs_result):
        assert relationship.type in docs_result
        for (key, value) in relationship.items():
            assert value in docs_result

    def is_property_in_result(self, key, value, docs_result):
        assert value in docs_result
