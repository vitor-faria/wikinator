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


def get_ontology(assertions=[], base_kind='dbo:Person', exclude_set={"owl:Thing"},  limit=200):
    select = "SELECT ?object (COUNT(?candidate) AS ?occurrences) "
    where = build_where_clause(
        assertions=assertions,
        base_kind=base_kind,
        extra_clause=" ?candidate a ?object. ",
    )
    group_by = "GROUP BY ?object "
    order_by = "ORDER BY DESC (?occurrences) "
    limit = f"LIMIT {limit}"
    query = select + where + group_by + order_by + limit
    print(query)
    df_results = pd.DataFrame(dbpedia_query(query))
    df_results['object'] = df_results['object'].str.replace(
        pat="http://dbpedia.org/ontology/",
        repl="dbo:",
    )
    for assertion in assertions:
        if isinstance(assertion, tuple):
            if assertion[0].startswith("a "):
                exclude_set.add(assertion[0].split("a ")[1])
        elif isinstance(assertion, str):
            if assertion.startswith("a "):
                exclude_set.add(assertion.split("a ")[1])
    print(exclude_set)
    df = df_results[
        (df_results['object'].str.count('dbo') > 0)
        & (~df_results['object'].isin(exclude_set))
    ]

    return df


def build_where_clause(assertions=[], base_kind='dbo:Person', extra_clause=''):
    assertions = [
        tuple_element for tuple_element in assertions if isinstance(tuple_element, tuple)
    ]
    true_assertions = [assertion for assertion, is_true in assertions if is_true]
    false_assertions = [assertion for assertion, is_true in assertions if not is_true]
    where_start = "WHERE { ?candidate a " + base_kind
    where_middle = " . "
    if true_assertions:
        where_middle = " ; " + " ; ".join(true_assertions) + " . "
    filter_not_exists = " "
    if false_assertions:
        filter_not_exists_start = "FILTER NOT EXISTS { ?candidate "
        filter_not_exists_end = " ; ".join(false_assertions) + " } "
        filter_not_exists = filter_not_exists_start + filter_not_exists_end

    return where_start + where_middle + filter_not_exists + extra_clause + " }"


def get_predicate_object(base_kind="dbo:Person", assertions=[], index=0):
    select = "SELECT ?predicate ?object (COUNT(?candidate) as ?occurrences) "
    where = build_where_clause(
        assertions=assertions,
        base_kind=base_kind,
        extra_clause=" ?candidate ?predicate ?object. ",
    )
    group_by = " GROUP BY ?predicate ?object "
    order_by = " ORDER BY DESC (?occurrences) "
    limit = " LIMIT 50 "
    query = select + where + group_by + order_by + limit
    print(query)
    df_results = pd.DataFrame(dbpedia_query(query))

    return order_by_relevance(df_results, index)


def order_by_relevance(df_results, index=0):
    optimal_occurrences = int(df_results.occurrences[index])/2
    df_results["normalized_occurrences"] = df_results["occurrences"].apply(
        lambda x: abs(int(x) - optimal_occurrences)
    )
    df_results.sort_values(by=['normalized_occurrences'], inplace=True)

    return df_results


def ask_predicate_from_df(df_results, base_kind='dbo:Person', row=0):
    question, predicate_object = '', ''
    if len(df_results) > row:
        base_kind = base_kind.split('dbo:')[1]
        question_start = f'Does this {base_kind} have '
        _predicate = str(df_results.iloc[row, 0])
        _object = str(df_results.iloc[row, 1])
        predicate_object = f"<{_predicate}> <{_object}>"
        question = f"{question_start} {_predicate} {_object}?"
        print(question)
        print(df_results.head())

    return question, predicate_object


def next_predicate_question(assertions, base_kind="dbo:Person", df_last_question=None, row_last_question=None):
    if len(assertions) > 0 and isinstance(assertions[-1], tuple):
        last_assertion, last_answer = assertions[-1]

        if any((last_assertion.startswith("a "), isinstance(last_answer, bool))):  # Next query
            df = get_predicate_object(base_kind, assertions, index=0)
            row = 0

        else:  # None == I don't know => Next row
            df = df_last_question
            row = row_last_question + 1

        question, predicate_object = ask_predicate_from_df(df, base_kind, row)
        if question:
            assertions.append(predicate_object)
            print(assertions)

        return question, assertions, df, row


def get_person_ontology(patterns: list = [], limit=200):
    exclude_list = {
        "dbo:Person",
        "dbo:Species",
        "dbo:Eukaryote",
        "dbo:Animal",
    }

    return get_ontology(patterns, 'dbo:Person', exclude_list, limit)


def get_character_ontology(patterns: list = [], limit=200):
    exclude_list = {
        "dbo:FictionalCharacter",
        "dbo:Agent",
    }

    return get_ontology(patterns, 'dbo:FictionalCharacter', exclude_list, limit)


def ask_ontology_from_df(df, base_kind='dbo:Person', row=0):
    question, ontology = '', ''
    if len(df) > row:
        base_kind = base_kind.split('dbo:')[1]
        question_start = f'Is this {base_kind} a '
        ontology = str(df.iloc[row, 0])
        question = question_start + ontology.split('dbo:')[1] + '?'
        print(question)
        print(df.head(10))

    return question, ontology


def next_person_ontology_question(assertions=[], df_last_question=None, row_last_question=None):
    if len(assertions) > 0:
        _, last_answer = assertions[-1]

        if last_answer:  # Next query
            df = get_person_ontology(assertions)
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
        assertions.append("a " + ontology)
        print(assertions)

    return question, assertions, df, row


def next_character_ontology_question(assertions=[], df_last_question=None, row_last_question=None):
    if len(assertions) > 0:
        _, last_answer = assertions[-1]

        if last_answer:  # Next query
            df = get_character_ontology(assertions)
            row = 0

        else:  # Next row
            df = df_last_question
            row = row_last_question + 1

    else:  # First question
        df = get_character_ontology()
        row = 0

    question, ontology = ask_ontology_from_df(df, base_kind='dbo:FictionalCharacter', row=row)

    if question:
        assertions.append("a " + ontology)
        print(assertions)

    return question, assertions, df, row


def save_answer(answer, assertions=[]):
    if isinstance(assertions[-1], str):
        assertions[-1] = assertions[-1], answer
        print(assertions)

    return assertions


def make_guess(assertions=[], base_kind='dbo:Person'):
    select = "SELECT ?candidate (COUNT(?subject) AS ?ingoing_links) "
    where = build_where_clause(
        assertions=assertions,
        base_kind=base_kind,
        extra_clause=" ?subject dbo:wikiPageWikiLink ?candidate . ",
    )
    group_by = "GROUP BY ?candidate "
    order_by = "ORDER BY DESC (?ingoing_links) "
    limit = f"LIMIT 10"
    query = select + where + group_by + order_by + limit
    print(query)
    df_results = pd.DataFrame(dbpedia_query(query))
    df_results['candidate'] = df_results['candidate'].str.replace(
        pat="http://dbpedia.org/resource/",
        repl="",
    ).str.replace(
        pat="_",
        repl=" ",
    )

    base_kind = base_kind.split('dbo:')[1]
    question = f'Is this {base_kind} ' + df_results['candidate'][0] + "?"

    return question, df_results
