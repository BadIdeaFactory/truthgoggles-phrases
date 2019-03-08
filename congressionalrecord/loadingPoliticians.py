import requests
import pandas as pd
import json
from bs4 import BeautifulSoup

def main():
    page = requests.get("https://ballotpedia.org/List_of_current_members_of_the_U.S._Congress")
    soup = BeautifulSoup(page.text, "html.parser")
    for body in soup("tbody"):
        body.unwrap()

    tables = pd.read_html(str(soup), flavor="bs4")

    pd.set_option('display.max_rows', len(tables[1]))

    senateData = {}
    houseData = {}

    currentSenate = tables[0]
    currentHouse = tables[1]
    print(currentSenate)

    createDictionaries(senateData, currentSenate)
    createDictionaries(houseData, currentHouse)

def createDictionaries(diction, dataTable):
    diction["politicians"] = []
    for i in range(1, len(dataTable)):
        name = dataTable[0][i]
        temp = dataTable[1][i]
        chamber = temp.split(" ")[1]
        if chamber == "Senate":
            representing = temp.replace("U.S. Senate ", "")
        else:
            representing = temp.replace("U.S. House ", "")
        party = dataTable[3][i]
        diction['politicians'].append({
            'name': name,
            'chamber': chamber,
            'constituency': representing,
            'party': party
        })

    with open(chamber+'Data.txt', 'w') as outfile:
        json.dump(diction, outfile)
        outfile.close()


main()