# For writing checkbox html for all hobbies
def getCategorized():
    f = open("categroized", "r")
    f = f.readlines()
    index = 0
    d = dict()
    n = ""
    arr = []
    while index < len(f):
        if f[index] == "\n" or f[index] == "]":
            index = index + 1
            continue
        if f[index][0:1] != " ":
            if n != "" and f[index][0:1] == "]":
                d[n] = arr
                arr = []
                index = index + 1
            else:
                n = f[index][0: f[index].index(" ")]
                index = index + 1
        else:
            t = f[index + 2].split("'alt': '")[1]
            t = t[0: len(t) - 3]
            arr.append(t)
            index = index + 6


    for i,j in d.items():
        print(i, j)

    pickle.dump(d, open("hobbiesCategorized.p", "wb"))

# To change it to write w/o the w3 format
def fixDiv():
    f = open("divs.txt", "r")
    lines = f.readlines()
    index = 0

    out = open("outputDiv.txt", "w")

    while index < len(lines):
        if '<!' in lines[index]:
            index = index + 2
        elif len(lines[index]) == 0 or '</div>' in lines[index] or lines[index] == "\n":
            # print(lines[index])
            index = index + 1
        else:
            # Transforms this:
            #<div class="w3-quarter">
            #     <img src="https://d1ynl4hb5mx7r8.cloudfront.net/wp-content/uploads/2019/03/12121626/801030334.7.fcstudio.ike_...oak_.brewery.katrina.whittkamp.jpg" alt="Breweries" style="width:100%">
            #     <h3>Breweries</h3>
            #     <p>A place where beer is made commercially</p>
            #     <input type="checkbox" value="51" name="mycheckbox">
            # </div>

            # To:
            # {
            #     'src': 'https://cdn.vox-cdn.com/thumbor/_Jlcsk7GFdFRDw6AoWq1l1B91tA=/1400x1050/filters:format(jpeg)/cdn.vox-cdn.com/uploads/chorus_asset/file/15089579/FO-Interior.0.0.1417716936.jpg',
            #     'alt': 'Gastropubs',
            #     'desc': 'A hybrid pub, bar and restaurant, notable for serving alcoholic drinks and food',
            #     'val': '2'
            # },

            src = lines[index + 1].split("<img src=\"")[1]
            src = src[0:src.index(' ') - 1]
            print(src)
            alt = lines[index + 2].strip()
            alt = alt[4:len(alt) - 5]
            desc = lines[index + 3].strip()
            desc = desc[3:len(desc) - 4]
            print(alt)
            print(desc)
            val = lines[index + 4].strip().split('<input type=\"checkbox\" value=\"')
            val = val[1]
            val = val[0:val.index("\"")]
            print(val)

            out.write("{\n")
            out.write("\t\'src\': \'" + src + "\',\n")
            out.write("\t\'alt\': \'" + alt + "\',\n")
            out.write("\t\'desc\': \'" + desc + "\',\n")
            out.write("\t\'val\': \'" + val + "\',\n")
            out.write("},\n")
            index = index + 6


# To write the checkbox html
def automate_html(fileName):
    try:
        ed = pickle.load(open("enumeratedData.p", "rb"))
    except:
        print("File couldn't be read")
        raise FileNotFoundError

    outputFile = open("outputHtml.txt", "w")
    for i,j in ed.items():
        outputFile.write("<li>" + j + "<input type=\"checkbox\" value=\"" + str(i) + "\" name=\"mycheckbox\"></li>\n")

    outputFile.close()