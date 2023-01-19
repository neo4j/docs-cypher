# Test criterias

Same info as below, but visually: https://miro.com/app/board/uXjVPxqGnVI=/?share_link_id=353162696775

Each adoc file is a _test_, and each example contained in the file is a _subtest_. Database is cleaned up between tests (but not subtests).

- If file has `:test-skip: true` directive, **skip**.
- If example has `test-skip` in its source tag (ex. `[source, cypher, role=test-skip]`), **skip**.
- If example has query parameters, **skip**.
- If example has csv loading, **skip** (although we could test if csv is at a public URL).
- If example has any of Cypher's untestable functions (either related to current time or to random returns) in its query, **skip**. The list `['date', 'datetime', 'localdatetime', 'localtime', 'time', 'timestamp', 'randomUUID', 'elementId']`. Fixed times are tested (or?).
- If example has no result attached in the docs and running the example does not raise an error, **pass**.
- If running the example fails, and example does not have `test-fail` in its source tag (ex. `[source, cypher, role=test-fail]`), **fail**.
- If example has a result attached in the docs, **pass** if all _property values_ returned by actually running the query are found in the docs output (all lowercase). For relationship objects, check that relationship type is also present.
`PROFILE` queries are validated by comparing the list of operators, in order.
- If example returns a `Path` object, **skip** (at least for now).

All in all, record types whose validation is supported are: `Node`, `Relationship`, `string`, `int`, `bool`, `list`.


# Usage
**You need a running Neo4j Enterprise Edition instance.**

Install required packages (once only):
```bash
pip install -r requirements.txt
```

Set your Neo4j password in the environment variables and run tests with:
```bash
export NEO4J_PASSWORD='verysecret'
pytest test-cypher.py --tb=short
```
where `--tb=short` will make the report for each error more succinct. For debugging, it can be useful to append `-s`, which will avoid pytest to buffer/suppress some output, and `-rs` to display info about skipped tests.


## Specify files to test

By default, all `.adoc` files in `modules/ROOT` are (recursively) gathered for testing.
You can provide a list of comma-separated paths to be tested through the environment variable `CYPHER_TEST_PATH`. Paths are recursively expanded through [`glob`](https://docs.python.org/3/library/glob.html), so you can use wildcards. Paths are either relative to the location where you run tests, or absolute.
For example, `export CYPHER_TEST_PATH='modules/ROOT/**/clauses/*.adoc, modules/ROOT/**/aliases.adoc'` will result in all clauses content AND the aliases page to be tested.

If Neo4j is not running on localhost, or if the username is not `neo4j`, you can specify different values:
```bash
export NEO4J_URI='neo4j+s://auradb.neo4j.com' NEO4J_USER='neo4p'
```

## Setup queries

**Queries that set the stage for the page examples** should appear before the examples that need the data, and **should be included in a `[source, cypher]` block**, optionally marked with `role=test-setup` (although, as of now, the marking has no special effect). Separate statements with a semicolon. If one query fails, all subsequent setup queries will be ignored, so it is important that the setup doesn't raise errors.
Hide them from display with `////` as an asciidoc comment.
For example,
```
////
[source, cypher, role=test-setup]
----
CREATE
  (charlie:Person {name: 'Charlie Sheen'}),
  (martin:Person {name: 'Martin Sheen'}),
  (michael:Person {name: 'Michael Douglas'});
CREATE (matrix:Movie {name: 'Matrix'});
----
////
````

# TO DO
- handle result types: Path, dict (,date?)
