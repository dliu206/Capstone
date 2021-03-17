from mlxtend.frequent_patterns import apriori, association_rules
import pickle
import numpy as np
import pandas as pd
import time

# Creates a pandas Dataframe from Merged data w/ Yelp classification
def legibile_dataFrame(fileName):
    try:
        data = pickle.load(open(fileName, "rb"))
    except:
        data = dict()

    s = set()
    for i, j in data.items():
        for item in j:
            if item not in s:
                s.add(item)

    indexData = dict()
    index = 0
    for item in s:
        indexData[item] = index
        index = index + 1

    header = list(s)
    newData = []
    for i, j in data.items():
        temp = np.zeros(len(s))
        for item in j:
            temp[indexData[item]] = 1
        newData.append(list(temp))
    data = pd.DataFrame(newData, columns=header)


    frq_items = apriori(data, min_support=0.002, use_colnames=True)
    rules = association_rules(frq_items, metric="lift", min_threshold=1)
    rules = rules.sort_values(['confidence', 'lift'], ascending =[False, False])
    print(rules)
    pickle.dump(rules, open("rules.p", "wb"))

    # Valid ant's
    temp_s = set()
    for item in rules.antecedents:

        for ant in item:
            if ant not in temp_s:
                temp_s.add(ant)

    d = dict()
    index = 1
    for ant in header:
        if ant in temp_s:
            d[index] = ant
        index = index + 1
    pickle.dump(d, open("enumeratedData.p", "wb"))

    for i,j in d.items():
        print(i,j)


# Generates links between antecedents to consequents
def generate_links():
    rules = pickle.load((open("rules.p", "rb")))
    ant = list(rules.antecedents)
    con = list(rules.consequents)
    sup = list(rules.support)
    # ant -> sup, con
    data = dict()
    index = 0
    for a in ant:
        for item in a:
            if item not in data:
                tup = ()
            else:
                tup = data[item]
            for consequent in con[index]:
                tup = tup + (consequent, sup[index])
            data[item] = tup
        index = index + 1
    pickle.dump(data, open("links.p", "wb"))

# generate_links()
enumData = "enumeratedData.p"
links_stuff = "links.p"
category_stuff = "hobbiesCategorized.p"

# Predicts based on hand made categories
# Returns top 3 values w/ support values
def predict(selectedList):
    try:
        enumeratedData = pickle.load(open(enumData, "rb"))
    except:
        print("Enumerated not detected")
        return
    for i,j in enumeratedData.items():
        print(i, j)

    try:
        links = pickle.load(open(links_stuff, "rb"))
    except:
        print("Links not detected")
        return

    try:
        categories = pickle.load(open(category_stuff, "rb"))
    except:
        print("Categories not detected")
        return
    # Gonna be in the format of item, support
    out = dict()

    for item in selectedList:
        # integer casting?
        hobby = enumeratedData[item]
        hobby = hobby.strip("\n")
        index = 0
        try:
            while index < len(links[hobby]):
                name = links[hobby][index]
                support = links[hobby][index + 1]
                index = index + 2
                if name not in out:
                    out[name] = support
                else:
                    if out[name] < support:
                        out[name] = support
        except:
            continue


    out = dict(sorted(out.items(), key=lambda item: item[1]))
    maxed = dict()
    for i,j in out.items():
        for cname in categories.keys():
            if i in categories[cname]:
                if cname not in maxed:
                    maxed[cname] = (i, j)
                continue
        print(i, j)
    for i, j in maxed.items():
        print(i, j)

    return maxed.values()

# Example where each number represents an index for a filtered hobby type
# print(predict([1, 187, 228]))
