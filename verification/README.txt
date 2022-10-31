# Cypher Documentation Tests


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

