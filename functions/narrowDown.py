import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON


def analyzeOccurences(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(query)

    resultSet = []

    try:
        queryResult = sparql.queryAndConvert()

        for res in queryResult['results']['bindings']:
            resultSet.append({"Object": res['object']['value'], "Predicate": res['predicate']
                             ['value'], "Occurences": int(res['occurences']['value'])})
    except Exception as e:
        print(e)

    orderByRelevance(resultSet)


def orderByRelevance(resultSet):
    optimalOccurences = resultSet[0]["Occurences"]/2

    for result in resultSet:
        result['Occurences'] = abs(optimalOccurences - result['Occurences'])

    resultSet = sorted(resultSet, key=lambda x: x['Occurences'])

    askNextQuestion(resultSet)


def askNextQuestion(resultSet):

    question = ("Does your character have the following relation: " +
                resultSet[0]["Predicate"].rsplit("/", 1)[-1] + " ---> " + resultSet[0]["Object"].rsplit("/", 1)[-1])
    answer = None

    extendWhereClause(resultSet[0]["Predicate"],
                      resultSet[0]["Object"], answer)


def extendWhereClause(predicate, object, answer):
    if (answer):
        whereCondition = "?x <" + predicate + "> <" + object + ">."
    else:
        filter = " FILTER NOT EXISTS(?x <" + predicate + "> <" + object + ">)."

    # Would now call first function again. Add filter or where Conditions first.
