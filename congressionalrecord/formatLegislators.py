import json
from stateAbbreviations import getStateAbbreviations

def main(oldFile, newFile):
    f = open(oldFile, 'r')
    writer = open(newFile, 'w')
    oldData = json.load(f)
    f.close()

    yearRange = range(2005, 2020)
    newData = {}
    for i in yearRange:
        newData[str(i)] = {}

    stateAbbreviations = getStateAbbreviations()

    for i in range(len(oldData)):
        if 'middle' in oldData[i]["name"].values():
            name = (oldData[i]["name"]['first']) + " " + (oldData[i]["name"]['middle']) + " " + (oldData[i]["name"]['last'])
        else:
            name = (oldData[i]["name"]['first']) + " " + (oldData[i]["name"]['last'])
        #name = oldData[1]["name"]["last"]
        name = stripForLetters(name)

        keyName = name.split(" ")[-1].lower()
        #print(name)

        startDate = oldData[i]['terms'][0]['start']
        startYear = int(startDate[:4])
        endDate = oldData[i]['terms'][-1]['end']
        endYear = int(endDate[:4])
        endYear = stripForNumbers(endYear)

        if (startYear not in yearRange):
            if (endYear not in yearRange and endYear < 2019):
                continue
        politician = {}
        politician['name'] = oldData[i]['name']
        politician['termsArr'] = oldData[i]['terms']

        if startYear in yearRange:
            rangeEnd = min(2020, endYear)
            for ny in range(startYear, rangeEnd):
                yearTerm = findTerm(politician['termsArr'], ny)
                house = yearTerm['type']
                politician['terms'] = yearTerm
                if keyName + ";" + house in newData[str(ny)]:
                    oldPolitician = newData[str(ny)][keyName + ";" + house]
                    oldPolState = (stateAbbreviations[oldPolitician['termsArr'][0]['state']]).lower()
                    newPolState = (stateAbbreviations[politician['termsArr'][0]['state']]).lower()
                    if oldPolState == newPolState:
                        continue
                    newData[str(ny)][keyName + " of " + oldPolState + ";" + house] = oldPolitician
                    newData[str(ny)].pop(keyName + ";" + house)
                    newData[str(ny)][keyName + " of " + newPolState + ";" + house] = politician
                    print(keyName + " of " + oldPolState + ";" + house + ";" + str(ny))
                    print(keyName + " of " + newPolState + ";" + house + ";" + str(ny))
                    print('\n\n')
                else:
                    newData[str(ny)][keyName + ";" + house] = politician
                    polState = (stateAbbreviations[politician['termsArr'][0]['state']]).lower()
                    newData[str(ny)][keyName + " of " + polState + ";" + house] = politician
        elif endYear in yearRange or endYear > 2019:
            rangeStart = max(startYear, 2005)
            rangeEnd = min(endYear, 2020)
            for ny in range(rangeStart, rangeEnd):
                yearTerm = findTerm(politician["termsArr"], ny)
                politician['terms'] = yearTerm
                house = yearTerm['type']
                temp = keyName + ";" + house
                if temp in newData[str(ny)]:
                    oldPolitician = newData[str(ny)][keyName + ";" + house]
                    oldPolState = (stateAbbreviations[oldPolitician['termsArr'][0]['state']]).lower()
                    newPolState = (stateAbbreviations[politician['termsArr'][0]['state']]).lower()
                    if oldPolState == newPolState:
                        continue
                    newData[str(ny)][keyName + " of " + oldPolState + ";" + house] = oldPolitician
                    newData[str(ny)].pop(keyName + ";" + house)
                    newData[str(ny)][keyName + " of " + newPolState + ";" + house] = politician
                else:
                    newData[str(ny)][keyName + ";" + house] = politician
                    polState = (stateAbbreviations[politician['termsArr'][0]['state']]).lower()
                    newData[str(ny)][keyName + " of " + polState + ";" + house] = politician


    json.dump(newData, writer)

    writer.close()


def stripForNumbers(phrase):
    word = ""
    for ch in str(phrase):
        if ch.isnumeric() or ch == " ":
            word += ch.lower()
    return int(word)

def stripForLetters(phrase):
    word = ""
    for ch in phrase:
        if ch.isalpha() or ch == " " or ch == "-" or ch == "'":
            word += ch.lower()
    return word

def findTerm(terms, year):
    for term in terms:
        yearStart = int(term['start'][:4])
        yearEnd = int(term['end'][:4])
        if year in range(yearStart, yearEnd):
            return term
    return {'type': "junk answer"}


main("legislators-historical.json", "historicalLegislators.json")
main("legislators-current.json", "currentLegislators.json")

