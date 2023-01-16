from neo4j import GraphDatabase
import re


URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secret")


def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)
    

def clean_database(driver):
    print("clean database")
    with driver.session(database='neo4j') as session:
        session.run("MATCH (_) DETACH DELETE _").consume()
        # should also delete indexes, constraints, etc


def extract_examples_from_asciidoc(asciidoc):
    """
    Extract a list of (tag, query, result) dicts from asciidoc input.

    Example of one dict item: {
      "tag": "[source, cypher, indent=0 role=test-skip]",
      "query": "MATCH (director {name: 'Oliver Stone'})--(movie) RETURN movie.title",
      "docs_result": "| +movie.title+
                      | +'Wall Street'+
                      1+d|Rows: 1"
    }
    """

    query_pattern = re.compile(r"""
    (?:                               # non-capturing group to match example opening
        (\[source,\s*cypher[^\]]*\])  # [source,cypher] and variations (whitespace, other attributes)
        \s*                           # line break and any white space
        -{4}                          # 4 opening dashes
        \s*                           # line break and any white space
    )
    (.*?)                             # CYPHER QUERY
    \s*                               # line break and any white space
    -{4}                              # 4 closing dashes
    """, re.MULTILINE | re.DOTALL | re.VERBOSE)
    # flat regex: (?:\[source,\s*cypher([^\]]*)\]\s*-{4}\s*)([^\$]*?)\s*-{4}
    
    result_pattern = re.compile(r"""
    (?:                               # non-capturing group to match result opening
        \[role="queryresult"[^\]]*\]  # [role="queryresult"] and variations (whitespace, other attributes)
        \s*                           # line break and any white space
        \|={3}                        # opening |===
        \s*                           # line break and any white space
    )
    (.*?)                             # QUERY RESULT
    \s*                               # line break and any white space
    \|\={3}                           # closing ===|
    """, re.MULTILINE | re.DOTALL | re.VERBOSE)
    #flat regex: (?:\[role="queryresult"[^\]]*\]\s*\|={3}\s*)(.*?)\s*\|\={3}

    # Search for a query, a result, and the _next_ query.
    # Pair query and result only if result occurs _before_ next query.
    examples = []
    location = 0  # keeps track of where the parser is
    while (query := query_pattern.search(asciidoc[location:])) is not None:
        result = result_pattern.search(asciidoc[location:])
        next_query = query_pattern.search(asciidoc[query.end():])

        if (result == None or
           (next_query != None and result.start() > next_query.start())):
            # result does not exist or does not belong to this query
            examples.append({
                'tag': query.group(1),
                'query': query.group(2),
                'docs_result': None
            })
            location += query.end()
        else:
            # result belongs to this query
            examples.append({
                'tag': query.group(1),
                'query': query.group(2),
                'docs_result': result.group(1)
            })
            location += result.end()

    return examples


def extract_plan_operators(query_plan):
    """
    Extract operator list from a query plan output.
    """

    operator_pattern = re.compile(r'\+([A-Za-z]+)')
    return operator_pattern.findall(query_plan)
