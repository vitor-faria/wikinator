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


def first_query_person(is_woman, is_alive):
    select = ""
    where = ""
    groupby = ""
    orderby = ""
    query = select + where + groupby + orderby

    return dbpedia_query(query)

