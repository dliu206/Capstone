import pickle
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
enumData = os.path.join(THIS_FOLDER, 'enumeratedData.p')
links_list = os.path.join(THIS_FOLDER, 'links.p')
category_list = os.path.join(THIS_FOLDER, 'hobbiesCategorized.p')

def predict(selectedList):
    try:
        enumeratedData = pickle.load(open(enumData, "rb"))
    except:
        print("Enumerated not detected")
        return
    for i,j in enumeratedData.items():
        print(i, j)

    try:
        links = pickle.load(open(links_list, "rb"))
    except:
        print("Links not detected")
        return

    try:
        categories = pickle.load(open(category_list, "rb"))
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
