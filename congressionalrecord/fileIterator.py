from stateAbbreviations import getStateAbbreviations
from politician import Politician
import os
import re
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import heapq

def main():
    rootdir = 'C:/Users/pouya\python-projects\congressional-record\congressionalrecord\output'
    writer = open("writer.txt", 'w')
    writer.close()
    dirtyWriter = open("dirtyWriter.txt", 'w')
    dirtyWriter.close()
    fullWriter = open("fullWriter.txt", 'w')
    fullWriter.close()
    speakerDict = {}
    numberOfDays = {"ignore this day"}
    wordStems = {}
    stopWords = set(stopwords.words('english'))
    newStopWords = [',', '...', 'congress', '', 'b', '.', '--', ':', ';', '$', '``', ')', '(', "''", 'year',
                    'the', "'s", 'c', 'a', 'also', '===============', '..', 'mr.', 'i', 'roll call',
                    'madam speaker', "public law", "section", "act", "sec", "secretary state", "made available",
                    "united states", "mr speaker", "remain available", "funds appropriated", "call roll"]
    stopWords.update(newStopWords)

    legislators = createLegislatorsDict()

    writer = open("legislator.json", 'w')
    json.dump(legislators, writer)
    writer.close()

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if file.endswith('.htm'):
                #yearGroup = re.search(r'\\20''[0-9]{2}', subdir)
                #year = yearGroup.group[0][1:] #stores year that speech was given.
                year = subdir[-15:-11]
                date = subdir[-10:-5] #stores date that speech was given
                """if int(date[:2]) == 1 and year%2 == 1:
                    if int(date[-2:]) < 3:
                        year-=1"""
                fname = subdir + '\\' + file
                numberOfDays.add(subdir)
                f = open(fname, 'r')
                contents = ""
                for line in f:
                    contents += line
                chamber = findChamber(os.path.join(file))
                f.close()
                contents = cleanContents(contents)
                dirtyWriter = open("dirtyWriter.txt", 'a')
                dirtyWriter.write(contents)
                dirtyWriter.close()
                contentList = cleanForSpeeches(contents)
                for r in contentList:
                    nameEnd = findNth(r, ".", 2)
                    name = r[0:nameEnd].lower()
                    if name not in speakerDict:
                        speakerDict[(name, chamber)] = list()
                    speakerDict[(name, chamber)].append((year, r[nameEnd:]))
    numberOfSpeeches = 0
    ps = PorterStemmer()
    wordCount = {}
    for speaker in speakerDict:

        speakerName = speaker[0]
        chamber = speaker[1]
        #print(speaker + ":    " + str(len(speakerDict[speaker])))
        numberOfSpeeches += len(speakerDict[speaker])
        if speaker not in wordStems:
            wordStems[speaker] = list()
        filteredSpeechWords = []
        nameToSearch = speakerName[speakerName.find(" ") + 1:]

        for tup in speakerDict[speaker]:
            speech = tup[1]
            year = tup[0]
            sp = ""
            for w in speech.split(" "):
                word = ""
                for ch in w:
                    if ch.isalpha() or ch == " ":
                        word += ch.lower()
                if word not in stopWords:
                    if not hasNumbers(word):
                        sp += (word + " ")
            sp = sp[:-1]
            filteredSpeechWords.append(sp)

            if (nameToSearch, chamber) in legislators[year]:
                # print(legislators[year][nameToSearch])
                pass
            else:
                print(speaker[0] + "      " + speaker[1] + "     " + str(year))
                print(speech + "\n\n")

        for speech in filteredSpeechWords:
            #if len(speakerDict[speaker]) == 1:
                #print(speech)
            bigrams = list(nltk.bigrams(speech.split()))
            speechWords = word_tokenize(speech)
            filteredSpeechWords = []
            for gram in bigrams:
                word = ""
                for w in gram:
                    word += (w + " ")
                word = word[:-1]
                if not hasNumbers(word):
                    if word not in stopWords:
                        filteredSpeechWords.append(word)

            """count = 0
            for phrase in filteredSpeechWords:
                wordArr = phrase.split(" ")
                for
                filteredSpeechWords[count] = ps.stem(w)
                count += 1"""
            wordStems[speaker].append(filteredSpeechWords)
            #print(filteredSpeechWords)
            for wo in filteredSpeechWords:
                #for wo in num:
                w = wo
                if (hasNumbers(w)):
                    continue
                if not w in wordCount:
                    wordCount[w] = 0
                wordCount[w] = wordCount[w] + 1
            #print(" ".join(speechWords))
            #TODO: Work on finishing this stemming

    #print(str(numberOfSpeeches) + " speeches over " + str(len(numberOfDays) - 1) + " days")
    printTopWords(wordCount)

def printTopWords(wordCount):
    topWords = []
    for w in wordCount:
        heapq.heappush(topWords, (-wordCount[w], w))
    counter = 0
    while counter < 100:
        clause = heapq.heappop(topWords)
        if not hasPhrase(clause):
            counter+=1
            #print(clause)

def findChamber(fname):
    chamberAbb = fname[fname.find("Pg") + 2:][: 1]
    switcher = {
        "H": "rep",
        "S": "sen",
        "E": "Unknown"
    }
    return switcher.get(chamberAbb, "Could Not Find")

def createLegislatorsDict():
    f = open("currentLegislators.json", "r")
    current = json.load(f)
    f.close()
    f = open("historicalLegislators.json", "r")
    historical = json.load(f)
    f.close()
    for year in current:
        for person in current[year]:
            if person in historical[year]:
                historical[year][person + " 2"] = current[year][person]
            else:
                historical[year][person] = current[year][person]

    return historical


def hasPhrase(phraseToCheck):
    phrasesCheckingFor = {"subsection", "sec", "act"}
    for word in phraseToCheck:
        if word in phrasesCheckingFor:
            return True
    return False

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def cleanContents(contents):
    bodystart = contents.index('<body>') + 6
    bodyend = contents.index('</body>')
    ret = contents[bodystart:bodyend]
    if (ret.index("<pre>") != -1):
        retstart = ret.index('<pre>') + 5
        retend = ret.index('</pre>')
        ret = ret[retstart:retend]
    return ret


def cleanForSpeeches(contents):
    record = ""
    recordList = []
    while (True):
        speaker = findSpeaker(contents)
        if ("2018\n" not in contents and "2019\n" not in contents and speaker not in contents):
            break
        else:
            prefixes = ["2018\n", "2019\n", speaker]
            spotToCheck = findFirstOcc(prefixes, contents, True)

            backgroundInfo = collectInfo(spotToCheck, contents) #gather speaker, state, chamber, and date

            contents = contents[spotToCheck:]
            possibleEnds = ["____________________", findSpeaker(contents[3:])]
            endSpot = findFirstOcc(possibleEnds, contents[3:]) #returns inf if not existent

            if endSpot == float('inf'):
                endSpot = len(contents)
            pageLoc = contents.find("[[Page ")
            while (pageLoc != -1):
                pageFinder = re.search('[[][[][P][a][g][e][ ].[0-9]+]]', contents)
                page = pageFinder.group(0)
                contents = contents.replace(page, '')
                pageLoc = contents.find("[[Page ")
            underscoreLoc = contents.find("______________")
            while (underscoreLoc != -1):
                underscoreFinder = re.search('[_]+', contents)
                underscore = underscoreFinder.group(0)
                contents = contents.replace(underscore, '')
                underscoreLoc = contents.find("______________")
            lineBreakLoc = contents.find("\n\n")
            while (lineBreakLoc != -1):
                contents = contents.replace("\n\n", "\n")
                lineBreakLoc = contents.find("\n\n")

            if (contents[0:1] == 'M'): #checks for if it is a speaker or a formality
                 if "[Roll No. " not in contents[:endSpot]:
                    recordList.append(contents[:endSpot])
                    record += contents[:endSpot]
            contents = contents[endSpot:]
            #print(" ".join(backgroundInfo))

    writer = open("writer.txt", 'a')
    for r in recordList:
        for ch in r:
            writer.write(ch)
        writer.write("\n\n\n")
    writer.close()
    return recordList

def collectInfo(num, contents):
    check = num
    date = ""
    speaker = ""
    chamber = ""
    state = ""
    lines = 0
    temp = 0
    while check >= 0:
        if contents[check] == "\n":
            lines += 1
            if lines%2 == 0:
                temp = check
            if lines == 3:
                date = contents[check:temp]
            if lines == 5:
                chamber = contents[check:temp].replace("in the ", "")
            if lines == 7:
                state = contents[check:temp].replace("of ", "")
            if lines == 9:
                speaker = contents[check:temp].replace("HON. ", "")
                break
        check -=1
    return [speaker, state, chamber, date]

def findSpeaker(contents):
    speakerSearch = re.search('[M][r,s]{1,2}'r'. ''[A-Z]+[.]', contents)
    #speakerSearch2 = re.search(r'  ''[M][r,s]{1,2}'r'. ''[A-Z]+[a-z]+[A-Z]+', contents)
    #loc = float('inf')
    #loc2 = float('inf')
    try:
        speaker = speakerSearch.group(0)
        #loc = contents.find(speaker)
    except:
        speaker = "zzzzzzzzzzzzzzzzzzz"

    """try:
        speaker2 = speakerSearch2.group(0)
        loc2 = contents.find(speaker2)
    except:
        speaker2 = "zzzzzzzzzzzzzzzzzzz"

    if min(speaker, speaker2) != -1 and min(speaker, speaker2) != float('inf'):
        print(min(speaker, speaker2))
    """

    return speaker

def findFirstOcc(array, contents, startBool = False):
    spotToCheck = float('inf')
    for prefix in array:
        temp = contents.find(prefix)
        if temp >= 0 and temp < spotToCheck:
            if startBool:
                if prefix == array[2]:
                    spotToCheck = temp
                else:
                    spotToCheck = temp + len(prefix) + 3
            else:
                spotToCheck = temp
    return spotToCheck

def findNth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

main()