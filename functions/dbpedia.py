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


def get_predicate_object(patterns: list = [], ontology_patterns='', exclude_list=[], where_middle="", filter="", index=""):
    select = "SELECT ?predicate ?object (COUNT(?x) as ?occurrences) "
    where_start = "WHERE {?x ?predicate ?object. "
    #where_middle = "; a " + "; a ".join(ontology_patterns) + ". "
    where_end = "} "
    where = where_start + ontology_patterns + where_middle + filter + where_end
    group_by = "GROUP BY ?predicate ?object "
    order_by = "ORDER BY DESC (?occurrences)"
    query = select + where + group_by + order_by
    print(query)
    df_results = pd.DataFrame(dbpedia_query(query))
    # exclude_list.extend(patterns)
    # df = df_results[
    #    (df_results['object'].str.count('dbo') > 0)
    #    & (~df_results['object'].isin(exclude_list))
    # ]

    return order_by_relevance(df_results, index)


def order_by_relevance(resultSet, index=0):

    optimalOccurences = int(resultSet.occurrences[index])/2

    for row in resultSet.iterrows():
        row[1][2] = abs(int(row[1][2]) - optimalOccurences)

    resultSet.sort_values(by=['occurrences'], inplace=True)
    resultSet.reset_index(drop=True, inplace=True)

    return ask_next_question(resultSet, index)


def ask_next_question(resultSet, index):
    question = ("Does your character have the following relation: " + resultSet.predicate[index].rsplit(
        "/", 1)[-1] + " ---> " + resultSet.object[index].rsplit("/", 1)[-1] + "?")

    return (question, resultSet.predicate[index], resultSet.object[index])


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


def ask_ontology_from_df(df, base_kind='dbo:Person', row=0):
    question, ontology = '', ''
    if len(df) > row:
        base_kind = base_kind.split('dbo:')[1]
        question_start = f'Is this {base_kind} a '
        ontology = str(df.iloc[row, 0])
        question = question_start + ontology.split('dbo:')[1] + '?'
        print(question)

    return question, ontology


def next_person_ontology_question(assertions=[], df_last_question=None, row_last_question=None):
    if len(assertions) > 0:
        _, last_answer = assertions[-1]

        if last_answer:  # Next query
            patterns = [question for question, answer in assertions if answer]
            df = get_person_ontology(patterns)
            row = 0

        else:  # Next row
            df = df_last_question
            row = row_last_question + 1

    else:  # First question
        df = get_person_ontology()
        row = 0

    question, ontology = ask_ontology_from_df(
        df, base_kind='dbo:Person', row=row)

    if question:
        assertions.append(ontology)

    return question, assertions, df, row


def save_answer(answer, assertions=[]):
    if isinstance(assertions[-1], str):
        assertions[-1] = assertions[-1], answer

    return assertions
