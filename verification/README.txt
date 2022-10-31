# Cypher Documentation Tests

The tests run pytest.

The fixture that get a specific Neo4j version is defined in:

```
docs-cypher/verification/tests/conftest.py
```

This fixture uses the testcontainers module to fetch a specific docker image of Neo4j and starts it and when all tests have run stops it.

https://github.com/testcontainers/testcontainers-python

The testcontainers module exposes a Neo4j driver also.


## Test examples


### tests/test_container.py

This is a simple example that show how to run a Cypher query.


### tests/test_match_clause.py

This is a WIP example to show how a Cypher query example should be tested.


### tests/test_query_plan_AllNodesScan.py

This is a WIP example to show how a query plan output should be tested.


## Python


Run all tests.

```
python -m tox
```

or

```
tox
```

### Check you python version

```
python --version
```

### Check where you python binary is located

```
which python
```

### Create a virtual environment named sandbox

```
python -m venv sandbox
```

### Activate the virtual environment named sandbox

```
source sandbox/bin/activate
```

### Deactivate the current active virtual environment

```
deactivate
```

### Upgrade pip

```
python -m pip install --upgrade pip
```

### Check whats is installed

```
python -m pip lists
```

### Install modules specified in a requirements file

```
python -m pip install -r requirements.txt
```


## Tests

### Run all tests

```
tox
```

### Run a specific test file

```
python -m pytest tests/test_container.py
```

### tox

https://tox.wiki/en/latest/

Recreate the environment if you change the tests/requirements.txt file.

```
tox --recreate
```

### Other

```
docker run --name neo4j --env NEO4J_AUTH=neo4j/pass -p7687:7687 --rm neo4j:latest
```

Check the health of the Neo4j instance

```
--health-cmd "cypher-shell -u neo4j -p ${password} 'RETURN 1'" \
    --health-interval 5s \
    --health-timeout 5s \
    --health-retries 5 \
```


## Style guide

https://google.github.io/styleguide/pyguide.html

https://docs.python.org/3/library/textwrap.html#textwrap.dedent


## Generate UUID

```
python uuid4.py
```

