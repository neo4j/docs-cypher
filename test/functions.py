import re

def clean_state(driver):
    print("clean database")
    with driver.session(database='neo4j') as session:
        session.run("MATCH (_) DETACH DELETE _").consume()


def extract_examples_from_asciidoc(asciidoc):
    # This pattern matches a query and a result found afterwards, skipping 
    # any content found in between. Source page should always contain a result
    # for each query. 
    # Expected input is an asciidoc file from the Neo4j Cypher manual.
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

    examples = []
    location = 0
    while (query := query_pattern.search(asciidoc[location:])) is not None:
        result = result_pattern.search(asciidoc[location:])
        next_query = query_pattern.search(asciidoc[query.end():])
        
        if result == None or result.start() > next_query.start():  # no result, or it belongs to next query
            examples.append((query.group(1), query.group(2), None))
            location += query.end()
        else:  # result is of this query
            examples.append((query.group(1), query.group(2), result.group(1)))
            location += result.end()

    #print(f'Found {len(examples)} examples in {filename}')
    return examples
