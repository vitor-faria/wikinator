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


def get_person_ontology(patterns: list = []):
    select = "SELECT ?object (COUNT(?x) AS ?occurrences) "
    where_start = "WHERE {?x a ?object ; a dbo:Person "
    where_middle = "; a " + "; a ".join(patterns) if len(patterns) > 0 else ""
    where_end = ". } "
    where = where_start + where_middle + where_end
    group_by = "GROUP BY ?object "
    order_by = "ORDER BY DESC (?occurrences)"
    limit = "LIMIT 200"
    query = select + where + group_by + order_by + limit
    print(query)
    df_results = pd.DataFrame(dbpedia_query(query))
    df = df_results[
        (df_results['object'].str.count('dbpedia.org/ontology') > 0)
        & (df_results['object'] != "http://dbpedia.org/ontology/Person")
        & (df_results['object'] != "http://dbpedia.org/ontology/Species")
        & (df_results['object'] != "http://dbpedia.org/ontology/Eukaryote")
        & (df_results['object'] != "http://dbpedia.org/ontology/Animal")
    ]

    return df

