import pandas as pd
import re
from collections import deque
import json

def getClassificationDict(df):
    columnDatatypeDict = df.dtypes.astype(str).to_dict()
    columnClassificationDict = {}
    for key, value in columnDatatypeDict.items():
        if value in columnClassificationDict:
            columnClassificationDict[value].append(key)
        else:
            columnClassificationDict[value] = [key]
    return columnClassificationDict
  
def getTokenValueAndDatatype(text):
    match = re.search(r"\{(.*?)\}", text)
    if match:
        token = match.group(1)
        return token.split(':')
    else:
        return None, None
      
def formatQuery(query, df):
    columnClassificationDict = getClassificationDict(df)
    tokenPattern = r'\{[^}]*\}'  # Matches any substring enclosed in {}
    queue = deque()
    result = []
    queue.append(query)
    while len(queue) > 0:
        frontQuery = queue[0]
        queue.popleft()
        match = re.search(tokenPattern, frontQuery)
        if match:
            firstToken = match.group(0)
            tokenValue, tokenDatatype = getTokenValueAndDatatype(firstToken)
            if tokenValue == 'column':
                for column in columnClassificationDict[tokenDatatype]:
                    tempQuery = re.sub(tokenPattern, column, frontQuery, count=1)
                    queue.append(tempQuery)
        else:
            result.append(frontQuery)
    return result
  
def generateQueries(queries, filename):
    df = pd.read_csv(filename)
    queryDict = {}
    for query in queries:
        queryDict[query] = formatQuery(query, df)
    return queryDict

# Template to generating queries
templateQueries = [
    "SELECT {column:object} where {column:int64} > [value:int64]",
    "SELECT {column:object},{column:int64} where {column:object} == [value:object]",
    "SELECT {column:object},{column:object} where {column:object} == [value:object] and {column:int64} > [value:object]"
]

# Generate queries for givem csv
queryDict = generateQueries(templateQueries, 'xyz.csv')
print(queryDict)

# Save queries to json file
with open('queries.json', 'w') as json_file:
    # Dump the dictionary into the file
    json.dump(queryDict, json_file)
