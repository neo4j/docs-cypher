To create a virtual environment named sandbox, use:

```
python -m venv sandbox
```

To activate the virtual environment named sandbox, use:

```
source sandbox/bin/activate
```

To deactivate the current active virtual environment, use:

```
deactivate
```

Upgrade pip

```
python -m pip install --upgrade pip
```

Install requirements

```
python -m pip install --requirement requirements.txt
```

```
python -m pip list
```

```
attrs      22.1.0
iniconfig  1.1.1
neo4j      4.4.5
packaging  21.3
pip        22.2.2
pluggy     1.0.0
py         1.11.0
pyparsing  3.0.9
pytest     7.1.2
pytz       2022.1
setuptools 58.1.0
tomli      2.0.1
```


Run integration tests

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


# tox

https://tox.wiki/en/latest/


# Style guide

https://google.github.io/styleguide/pyguide.html

https://docs.python.org/3/library/textwrap.html#textwrap.dedent



