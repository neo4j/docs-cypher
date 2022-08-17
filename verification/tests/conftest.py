# pytest conftest.py file

import pytest
import logging
import testcontainers.neo4j as tc

from textwrap import dedent

log = logging.getLogger()

neo4j_versions = {
    "4.4.10": "neo4j:4.4.10-enterprise", # 2022-08-09
    "4.3.16": "neo4j:4.4.16-enterprise", # 2022-08-09
}

VERSION = "4.4.10"

@pytest.fixture(autouse=False, scope="session")
def neo4j_container(request):
    # Session fixtures are shared among all tests during a pytest execution (pytest session).
    # Create a fixture starting up the Docker container, and shutting it down once the pytest session ends.

    docker_image = neo4j_versions.get(VERSION)

    log.info("[fixture] starting neo4j test container {}".format(docker_image))

    # docker run --name example-neo4j -p7687:7687 -p7474:7474 -p7473:7473 \
    # --env NEO4J_AUTH=neo4j/password \
    # --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    # neo4j:4.4.10-enterprise

    neo4j = tc.Neo4jContainer(image=docker_image)

    neo4j.env["NEO4J_ACCEPT_LICENSE_AGREEMENT"] = "yes"
    log.info("env {}".format(neo4j.env))
    log.info("ports {}".format(neo4j.ports))
    log.info("volumes {}".format(neo4j.volumes))
    log.info(neo4j.image)

    neo4j.start() # https://github.com/testcontainers/testcontainers-python/blob/master/testcontainers/core/container.py#L51

    def stop_neo4j():
        #driver.close()
        log.info("[fixture] stopping neo4j test container")
        try:
            neo4j.stop()
        except AttributeError as e:
            log.error(e)
        log.info("[fixture] neo4j test container stopped")

    request.addfinalizer(stop_neo4j)

    return neo4j

