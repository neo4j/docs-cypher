# Pytest

https://docs.pytest.org/


## pytest.ini

This file defines how to test and output results.
https://docs.pytest.org/en/7.2.x/reference/customize.html#configuration-file-formats


## conftest.py
This file defines top level resources/fixtures for the pytest tests.
https://docs.pytest.org/en/7.2.x/example/special.html#a-session-fixture-which-can-look-at-all-collected-tests
neo4j_container: get neo4j driver connect to DBMS
before_cleanup: clean up database before we run each test_*.py file