# pytest conftest.py file
import pytest
import logging
import testcontainers.neo4j as tc

log = logging.getLogger()

neo4j_versions = {
    "4.4.10": "neo4j:4.4.10-enterprise", # 2022-08-09
    "4.3.16": "neo4j:4.4.16-enterprise", # 2022-08-09
}

VERSION = "4.4.10"

# create docker instance, and get neo4j driver
# run before and after the while test job
@pytest.fixture(autouse=False, scope="session")
def neo4j_container(request):
    docker_image = neo4j_versions.get(VERSION)

    log.info("[fixture] starting neo4j test container {}".format(docker_image))

    neo4j = tc.Neo4jContainer(image=docker_image)

    neo4j.env["NEO4J_ACCEPT_LICENSE_AGREEMENT"] = "yes"
    log.info("env {}".format(neo4j.env))
    log.info("ports {}".format(neo4j.ports))
    log.info("volumes {}".format(neo4j.volumes))
    log.info(neo4j.image)

    neo4j.start()

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

# clean up database before test run, run before each test_*.py file start
@pytest.fixture(autouse=False, scope="module")
def before_cleanup(neo4j_container):
    driver = neo4j_container.get_driver()
    with driver.session() as session:
        session.run("MATCH (_) DETACH DELETE _").consume()
    log.info('Cleaing before each test run')
    driver.close()