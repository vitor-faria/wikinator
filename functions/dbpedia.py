import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON


def dbpedia_query(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    all_results = []

    try:
        results = sparql.queryAndConvert()
        bindings = results['results']['bindings']
        keys = bindings[0].keys()
        for binding in bindings:
            record = {}
            for key in keys:
                record[key] = binding[key]["value"]
            all_results.append(record)

    except Exception as e:
        print(e)

    return all_results


def get_ontology(patterns: list = [], base_kind='dbo:Person', exclude_list=[],  limit=200):
    select = "SELECT ?object (COUNT(?x) AS ?occurrences) "
    where_start = "WHERE {?x a ?object "
    patterns.append(base_kind)
    where_middle = "; a " + "; a ".join(patterns)
    where_end = ". } "
    where = where_start + where_middle + where_end
    group_by = "GROUP BY ?object "
    order_by = "ORDER BY DESC (?occurrences)"
    limit = f"LIMIT {limit}"
    query = select + where + group_by + order_by + limit
    print(query)
    df_results = pd.DataFrame(dbpedia_query(query))
    df_results['object'] = df_results['object'].str.replace(
        pat="http://dbpedia.org/ontology/",
        repl="dbo:",
    )
    exclude_list.extend(patterns)
    df = df_results[
        (df_results['object'].str.count('dbo') > 0)
        & (~df_results['object'].isin(exclude_list))
    ]

    return df


def get_person_ontology(patterns: list = [], limit=200):
    exclude_list = [
        "dbo:Person",
        "dbo:Species",
        "dbo:Eukaryote",
        "dbo:Animal",
    ]

    return get_ontology(patterns, 'dbo:Person', exclude_list, limit)


def get_character_ontology(patterns: list = [], limit=200):
    exclude_list = [
        "dbo:FictionalCharacter",
        "dbo:Agent",
    ]

    return get_ontology(patterns, 'dbo:FictionalCharacter', exclude_list, limit)

