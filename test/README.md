# Test criterias

Each adoc file is a _test_, and each example contained in the file is a _subtest_. Database is cleaned up between tests (but not subtests).

- If file has `:test-skip: true` directive, **skip**.
- If example has `test-skip` in its source tag (ex. `[source, cypher, role=test-skip]`), **skip**.
- If example has query parameters, **skip**.
- If example has csv loading, **skip** (although we could test if csv is at a public URL).
- If example has any of Cypher's untestable functions (either related to current time or to random returns) in its query, **skip**. The list `['date', 'datetime', 'localdatetime', 'localtime', 'time', 'timestamp', 'randomUUID', 'elementId']`. Fixed times are tested.
- If example has no result attached in the docs and running the example does not raise an error, **pass**.
- If running the example fails, and example does not have `test-fail` in its source tag (ex. `[source, cypher, role=test-fail]`), **fail**.
- If example has a result attached in the docs, **pass** if all _property values_ returned by actually running the query are found in the docs output (all lowercase). For relationship objects, check that relationship type is also present.
`PROFILE` queries are validated by comparing the list of operators, in order.
- If example returns a `Path` object, **skip** (at least for now).

All in all, record types whose validation is supported are: `Node`, `Relationship`, `string`, `int`, `bool`, `list`.

# Usage

```bash
python -m venv testing_env
source testing_env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd test
pytest test-cypher.py -rs -v
```

This will currently files as specified in the `filenames` var in `test-cypher.py`.

**Queries that set the stage for the page examples** should appear before the examples that need the data, and **should be included in a `[source, cypher]` block**, optionally marked with `role=test-setup` (although, as of now, the marking has no special effect).
Hide them from display with `////` as an asciidoc comment.
For example,

```
////
[source, cypher, role=test-setup]
----
CREATE
  (charlie:Person {name: 'Charlie Sheen'}),
  (martin:Person {name: 'Martin Sheen'}),
  (michael:Person {name: 'Michael Douglas'})
----
////
````

### TO DO
- command line argument for running on a list of files
- command line argument for running on a directory
- command line argument to specify docker image?
- take neo4j credentials from ENV variables?
- clean_database should clear everything, including indexes, alias, etc
- handle result types: Path
