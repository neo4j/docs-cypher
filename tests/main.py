# import pytest
import testcontainers.neo4j as tc


neo4j_versions = {
        "4.4.10": "neo4j:4.4.10-enterprise", # 2022-08-09
        "4.3.16": "neo4j:4.4.16-enterprise", # 2022-08-09
    }



# ID: 1234
# cypher-manual/
def test_return_nodes():
    with tc.Neo4jContainer() as neo4j:
        with neo4j.get_driver() as driver:

            #Validation of existence of text in a particular page:

            #docs-cypher/modules/ROOT/pages/clauses/return.adoc

            # Example: initial state
            #
            # CREATE
            #   (n1: {age: 55, happy: 'Yes!' name: 'A'}-[r1:BLOCKS]->(n2: )),
            #   (n1)-[r2:KNOWS]->(n2)")

            #setup cypher
            with driver.session() as session:
                result = session.run("CREATE (n1: {age: 55, happy: 'Yes!' name: 'A'}-[r1:BLOCKS]->(n2: )), (n1)-[r2:KNOWS]->(n2)")
                record = result.consume()

            #Validation of existence of text in a particular page:

            #docs-cypher/modules/ROOT/pages/clauses/return.adoc

            # Example: cypher
            #
            # MATCH (n {name: 'B'})
            # RETURN n

            #actual test
            #assert the output
            with driver.session() as session:
                result = session.run("MATCH (n) {name: 'B'} RETURN n")
                record = result.single()
                print(record)
                print("exit 2")

            #Validation of existence of text in a particular page:

            #docs-cypher/modules/ROOT/pages/clauses/return.adoc

            # Example: output
            #
            # +------------------+
            # | n                |
            # +------------------+
            # | Node({name:"B"}) |
            # +------------------+


def example():
    with tc.Neo4jContainer() as neo4j:
        with neo4j.get_driver() as driver:

            #setup cypher
            with driver.session() as session:
                result = session.run("CREATE (n:Example {yo: 'example'}) RETURN n")
                record = result.single()
                print(record)
                print("exit 1")

            #example cypher
            #example syntax

            #actual test
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN n LIMIT 1")
                record = result.single()
                print(record)
                print("exit 2")

            #assert the output

            #exampleoutput




#def example2():
#    with tc.Neo4jContainer(image=neo4j_versions["4.4.10"]) as neo4j:
#        with neo4j.get_driver() as driver:
#            with driver.session() as session:
#                #result = session.run("CREATE (n:Example:A {name: 'neo4j'})")
#                #_ = result.consume()

#                result = session.run("MATCH (n) RETURN n LIMIT 1")
#                record = result.single()
#                print(record)
#                print("exit")
#                #for record in result:
#                #    print(record)


if __name__ == "__main__":
    print("__main__")

    #print(neo4j_versions["4.4.10"])
    example()
