# from stateAbbreviations import getStateAbbreviations
# from politician import Politician
import os
import re
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import heapq


def main():
    rootdir = 'C:/Users/pouya\python-projects\\truth-goggles-phrases\congressionalrecord\output'
    recompileWriter = True
    """if recompileWriter:
        # resets the files to be empty to run our new program
        writer = open("writer.txt", 'w')
        writer.close()
        dirtyWriter = open("dirtyWriter.txt", 'w')
        dirtyWriter.close()
        fullWriter = open("fullWriter.txt", 'w')
        fullWriter.close()"""
    numberOfDays = 0  # keeps track of the number of days that speeches are given over
    wordStems = {}  # dictionary of all the stemmed words said and the number of times they are said
    stopWords = set(stopwords.words('english'))
    newStopWords = ['congress', '', 'b', 'year', 'the', "'s", 'c', 'a', 'also', 'mr', 'ms', 'mrs', 'i', 'roll call',
                    'madam', "public law", "section", "act", "sec", "secretary state", "made available",
                    "united states", "remain available", "funds appropriated", "call roll", "new york",
                    "my time", "yield", "bill", "subsection", "sec", "act", "usc", "et", "seq", "committee",
                    "speaker", "dr", "hr", "today", "alabama","alaska", "arizona", "srkansas", "california", "colorado",
                    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", "illinois",
                    "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
                    "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana",
                    "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
                    "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
                    "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah",
                    "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming", "gentleman",
                    "would", "north", "south", "may", "time", "house", "republican", "democrats", "president", "ask",
                    "dont", "thank", "make", "like", "ab", "pro", "pro tempore", "senate", "r", "congressman", "soon",
                    "met", "goes", "acts", "example", "fff", "bill", "act", "obama", 'v']
    stopWords.update(newStopWords)  # updates stop words to include congressional stop words
    peopleNotIn = 0  # counts how many people that politicians that speak cannot be found in our legislators dictionary

    # creates dictinoary of legislators to cross-reference for party and chamber
    legislators = createLegislatorsDict()
    writer = open("legislator.json", 'w')
    json.dump(legislators, writer)
    writer.close()

    # if we want to re-parse/clean the congressional record, this builds the dictionary of speakers and speeches
    # builds dictionary where key is a speaker and value is an array of all of their speeches
    if recompileWriter:
        speakerDict = buildWriterFile(rootdir)

    # if we don't want to re-clean the congressional record, this builds the dictionary of speakers and speeches
    else:
        speakerDict = parseWriterFile()

    numberOfSpeechesDems = 0  # stores number of speeches given by Dems
    numberOfSpeechesGop = 0  # stores number of speeches given by GOP
    ps = PorterStemmer()  # intiializes stemming object
    nonpartisanWordCounts = []  # maintains a count of all words said, regardless of party
    democratWordCounts = []  # maintains a count of all words said by Demcrats

    # stores a count of every word and bigram said and whether it is used more by republicans or democrats
    wordsWoStopWords = {}
    wordCountsList = []
    for i in range(26):
        wordsCounts.append({})
        democratWordCounts.append({})
        nonPartisanWordCounts.append({})

    for speaker in speakerDict:  # iterates through the speakers of all speeches

        # an array maintaining every speech given by speaker, after removing stop words, and the year it was given
        filteredSpeechWords = []

        speakerArr = speaker.split(";")  # list that has [name of speaker (+ "of " + their state), chamber]
        speakerName = speakerArr[0]  # stores speaker's name
        chamber = speakerArr[1]  # stores whether speaker in senate or house
        if speaker not in wordStems:
            wordStems[speaker] = list()  # adds speaker to wordStems if not already in it
        nameToSearch = speakerName[speakerName.find(" ") + 1:]  # name of speaker without prefix
        speakerDictKey = speaker.split(".")[-1].lower()[1:]  # stores name of spekaer without prefix and their chamber

        for tup in speakerDict[speaker]:
            speech = tup[1]  # stores speech given by speaker
            year = tup[0]  # stores year that speech was given
            sp = ""  # stores the speech given after removing stop words

            # finds party of speaker and assigns "not found" if cannot find speaker
            try:
                speakerParty = legislators[year][speakerDictKey]['terms']['party'].lower()
            except:
                speakerParty = "not found"

            for w in speech.split(" "):

                checkPhrase = True  # boolean that checks to see if we should skip the phrase if it contains a stop word
                word = ""  # stores each word after removing non-alpha and non-space characters.
                for ch in w:  # removes non-alpha and non-space characters from words
                    if ch.isalpha() or ch == " ":
                        word += ch.lower()
                if word not in stopWords:  # filters to remove stop words
                    wordArr = word.split(" ")
                    word = ""
                    for wordToCheck in wordArr:
                        if wordToCheck not in stopWords:
                            stemmedWord = ps.stem(w)
                            word = stemmedWord + " "
                        else:
                            word = ""
                            checkPhrase = False

                    if not checkPhrase:  # as long as the word is not in stopWords, keep going
                        continue

                    if not hasNumbers(word):  # filters to remove numbers and words containing numbers, e.g.
                        wo = word
                        word = ""
                        for ch in wo:
                            if ch.isalpha() or ch == " ":
                                word += ch.lower()

                        sp += word  # adds word to filtered speech

                        word = word.strip()
                        placeInArr = ord(word[0]) - ord('a')

                        if word not in nonpartisanWordCounts[placeInArr]:
                            # adds word to dictionary of non-partisan word counts if not in it
                            nonpartisanWordCounts[placeInArr][word] = 0

                        # increases count of word in non-partisan word count dict
                        nonpartisanWordCounts[placeInArr][word] = nonpartisanWordCounts[placeInArr][word] + 1

                        if word not in wordsWoStopWords[placeInArr]:
                            wordsWoStopWords[placeInArr][word] = 0  # adds word to dictionary of partisan word counts if not in it

                        # adds the word to the dictionary containing a count of words spoken by Democrats
                        if word not in democratWordCounts[placeInArr]:
                            democratWordCounts[placeInArr][word] = 0

                        # increases count if dem said word the word
                        if speakerParty == "democrat":
                            wordsWoStopWords[placeInArr][word] = wordsWoStopWords[placeInArr][word] + 1
                            democratWordCounts[placeInArr][word] = democratWordCounts[placeInArr][word] + 1

                        # decreases count if gop said word the word
                        elif speakerParty == "republican":
                            wordsWoStopWords[placeInArr][word] = wordsWoStopWords[placeInArr][word] - 1

            sp = sp[:-1]  # removes extra space at end of speech
            filteredSpeechWords.append((sp, year))  # adds speech and year to list of filtered speeches

            # checks to see if speaker is in our legislators database and maintains count of speakers not in it
            if (nameToSearch + ";" + chamber) in legislators[year]:
                pass
            else:
                peopleNotIn += 1
                print(nameToSearch + ";" + chamber + "     " + str(year))

        numberOfSpeechesBoolean = True  # helper boolean to keep track of number of speeches we parse
        for entry in filteredSpeechWords:
            speech = entry[0]  # filtered speech
            year = entry[1]  # year of speech

            # finds party of speaker and assigns "not found" if cannot find speaker
            try:
                speakerParty = legislators[year][speakerDictKey]['terms']['party'].lower()
            except:
                speakerParty = "not found"

            # adds the number of speeches given by the speaker to the appropriate party's speech count
            if numberOfSpeechesBoolean:
                if speakerParty == "democrat":
                    numberOfSpeechesDems += len(speakerDict[speaker])
                elif speakerParty == "republican":
                    numberOfSpeechesGop += len(speakerDict[speaker])
            numberOfSpeechesBoolean = False

            bigrams = list(nltk.bigrams(speech.split()))  # creates a list of all bigrams in the filtered speech
            removeWordThreshold = 1/8
            for gram in bigrams:
                word = ""  # stores the bigram as a string
                skip = False  # if True, should skip the bigram because it contains a stop word
                for w in gram:
                    if w in stopWords:
                        skip = True
                    word += (w + " ")  # creates the bigram as a string
                if skip:
                    continue  # does nothing with the bigram if it contains a stop word
                word = word[:-1]  # gets rid of the space on the end of the bigram string
                if not hasNumbers(word):  # skips the bigram if it contains a number
                    if word not in stopWords:  # skips the bigram if it is in the stop words
                        placeInArr = ord(word[0]) - ord('a')

                        # adds the word to the dictionary containing a count of words with partisan association
                        if word not in wordsWoStopWords[placeInArr]:
                            wordsWoStopWords[placeInArr][word] = 0

                        # adds the word to the dictionary containing a count of words without partisan association
                        if word not in nonpartisanWordCounts[placeInArr]:
                            nonpartisanWordCounts[placeInArr][word] = 0

                        # adds the word to the dictionary containing a count of words spoken by Democrats
                        if word not in democratWordCounts[placeInArr]:
                            democratWordCounts[placeInArr][word] = 0

                        # adds 1 to the count of the word without a partisan association
                        nonpartisanWordCounts[placeInArr][word] = nonpartisanWordCounts[placeInArr][word] + 1

                        # adds 1 to the count of the word with partisan association
                        if speakerParty == "democrat":
                            wordsWoStopWords[placeInArr][word] = wordsWoStopWords[placeInArr][word] + 1
                            democratWordCounts[placeInArr][word] = democratWordCounts[placeInArr][word] + 1
                        elif speakerParty == "republican":
                            wordsWoStopWords[placeInArr][word] = wordsWoStopWords[placeInArr][word] - 1

                        """if p percent of the time that a word occurs is within a bigram, we remove the individual word
                        from our word count dictionaries"""
                        for w in gram:
                            try:
                                bigramMentions = nonpartisanWordCounts[placeInArr][word])
                                singleWordMentions = nonpartisanWordCounts[placeInArr][w]
                                frequencyOfWord = bigramMentions/singleWordMentions
                                if frequencyOfWord > removeWordThreshold:
                                    nonpartisanWordCounts[placeInArr].pop(w)
                                    wordsWoStopWords[placeInArr].pop(w)
                                    democratWordCounts[placeInArr].pop(w)
                            except:
                                pass

    democratFrequencies = {}
    republicanFrequencies = {}
    minimumOccurunces = 150
    for word in nonpartisanWordCounts:
        totalMentions = nonpartisanWordCounts[word]
        if totalMentions >= minimumOccurunces:
            democratMentions = democratWordCounts[word]
            republicanMentions = totalMentions - democratMentions
            democratFrequencies[word] = democratMentions/totalMentions
            republicanFrequencies[word] = republicanMentions/totalMentions
            if word == "aerodrom":
                print(str(democratMentions) + "    " + str(totalMentions))
                print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    print(str(numberOfSpeechesDems) + " speeches from Dems over " + str(numberOfDays) + " days")
    print(str(numberOfSpeechesGop) + " speeches from GOP over " + str(numberOfDays) + " days")
    print(peopleNotIn)

    # prints the words that have the greatest magnitude of difference between times parties said word
    printTopWords(wordsWoStopWords, 1000)

    print("\n\n\n non-partisan word Counts: \n")
    printTopWords(nonpartisanWordCounts, 1000)  # prints the words that are said most regardless of party

    print("\n\n\n Democrat word Counts: \n")
    printTopWords(democratWordCounts, 1000)  # prints the words that are said most by Democrats

    printTopFrequencies(republicanFrequencies, nonpartisanWordCounts, 1000, "republicans")
    printTopFrequencies(democratFrequencies, nonpartisanWordCounts, 1000, "democrats")

def parseWriterFile():
    # TODO: implement this method!!

    # uncomment stuff below relating to counter and mod and lists wihtin contentList if the array gets too large
    speakerDict = {}
    contents = ""
    contentList = []
    # counter = 0
    followsLineBreak = False
    f = open("writer.txt", "r")
    for line in f:
        # mod = counter % 100
        # if mod == 0:
        #    contentList.append([])
        holder = line
        contents += holder
        if followsLineBreak:
            followsLineBreak = False
            if holder == "\n":
                # contentList[len(contentList-1)].append(contents)
                contentList.append(contents)
                contents = ""
        elif holder == "\n":
            followsLineBreak = True
        # counter += 1
    f.close()

    for r in contentList:
        nameEnd = findNth(r, ".", 2)  # finds the length of the speaker's name
        name = r[0:nameEnd].lower()  # stores the name of the speaker including their prefix
        speechLen = len(r)
        year = r[speechLen-6:speechLen-2]
        chamber = r[speechLen-10:speechLen-7]

        if name+";"+chamber not in speakerDict:
            speakerDict[name+";"+chamber] = list()

        if nameEnd != -1:
            speech = r[nameEnd:]
        else:
            continue
            # was "speech = ''"

        # appends the year and the speech to the speaker's list of speeches
        speakerDict[name + ";" + chamber].append((year, speech))
        # was "speakerDict[name + ";" + chamber].append((year, r[nameEnd:))"

    return speakerDict


def buildWriterFile(rootdir):
    speakerDict = {}
    for subdir, dirs, files in os.walk(rootdir):  # iterates through all congressional records
        for file in files:
            if file.endswith('.htm'):  # ensures that we only parse html files

                year = subdir[-15:-11]  # stores year that speech was given
                date = subdir[-10:-5]  # stores date that speech was given
                # month = date[:2]  # stores month that speech was given
                print(date + " in year " + year)

                """
                # GET RID OF THIS FOR FINAL ANALYSIS
                if int(year) < 2017:
                    break
                """

                fname = subdir + '\\' + file
                f = open(fname, 'r')  # opens file that contains speech
                contents = ""  # stores contents of html file
                for line in f:
                    contents += line
                f.close()
                chamber = findChamber(subdir + "\\" + file)  # stores whether speech given in house or senate
                contents = cleanContents(contents)  # gets rid of html jargon stored in speech
                """dirtyWriter = open("dirtyWriter.txt", 'a')
                dirtyWriter.write(contents)
                dirtyWriter.close()"""

                # stores a list of all the speeches given in the html file
                contentList = cleanForSpeeches(contents, year, True)

                for r in contentList:
                    nameEnd = findNth(r, ".", 2)  # finds the length of the speaker's name
                    name = r[0:nameEnd].lower()  # stores the name of the speaker including their prefix
                    if (name + ";" + chamber) not in speakerDict:
                        speakerDict[name + ";" + chamber] = list()  # adds speaker to speakerDict if not in it

                    # appends the year and the speech to the speaker's list of speeches
                    speakerDict[name + ";" + chamber].append((year, r[nameEnd:]))

    return speakerDict


def printTopFrequencies(wordCount, totalMentions, howMany, party):
    topWords = []  # heap of all of the words

    for w in wordCount:
        heapq.heappush(topWords, (-wordCount[w], w, totalMentions[w]))

    # prints the words that have the greatest magnitude of difference between times parties said word
    counter = 0
    stringToWrite = ""
    while counter < howMany:
        clause = heapq.heappop(topWords)
        counter += 1
        stringToWrite = (stringToWrite + str(clause[0]) + " " + clause[1] + " " + str(clause[2]) + "\n")
        if clause[0] > .5 and " " in clause[1]:
            print(clause[1])
    f = open(party+"Frequencies.txt", "w")
    f.write(stringToWrite)
    f.close()


def printTopWords(wordCount, howMany):
    """
    prints the words magnitude of difference between times parties said word and that magnitude
    :param wordCount: Dictionary that contains words or bigrams and the number of times they are said
    :param howMany: int denoting how many of the most occurring words to print
    :return: None
    """

    topWords = []  # heap of all of the words

    """initializes the heap with a tuple: (magnitude of difference between times parties said word,
    the word, which party said the word more)"""
    for w in wordCount:
        if wordCount[w] < 0:
            heapq.heappush(topWords, (wordCount[w], w, "republicans"))
        else:
            heapq.heappush(topWords, (-wordCount[w], w, "democrats"))

    # prints the words that have the greatest magnitude of difference between times parties said word
    counter = 0
    while counter < howMany:
        clause = heapq.heappop(topWords)
        counter += 1
        print(clause)

    # TODO: find a way to only print individual words if they are not part of a bigram that also occurs often


def findChamber(fname):
    """
    returns the chamber where the congressional record that is passed in is from
    :param fname:
    :return: String containing the chamber where the congressional record is from
    """

    chamberAbb = fname[fname.find("Pg") + 2:][: 1]  # gets what chamber the file address lists the record as from
    if chamberAbb == "H":
        return "rep"
    elif chamberAbb == "S":
        return "sen"
    elif chamberAbb == "D":
        return "not found"
    elif chamberAbb == "E":
        return findEChamber(fname)  # finds the chamber when the file is an extension of remarks from a chamber
    return "Could Not Find"  # returns "Could Not Find" if none of the other instances are true


def findEChamber(fname):
    """
    returns the chamber where the extension of the congressional record that is passed in is from
    :param fname:
    :return: String containing the chamber where the extension of the congressional record is from
    """

    # loads in the contents from the file
    f = open(fname, 'r')
    contents = ""
    for line in f:
        contents += line
    f.close()

    # cleans the file contents to only contain the speeches
    contents = cleanContents(contents)
    # cleanedContents = cleanForSpeeches(contents, "0", False)

    # strips contents down to only contain the line that contains the chamber of the record
    contents = contents[contents.find("in the"):]
    contents = contents[:contents.find("\n")]

    chamber = contents.split(" ")[-1]  # stores the chamber that the record is from

    # returns "rep" if the record is from the house and "sen" otherwise
    if chamber[:3] == "rep":
        return "rep"
    elif chamber[:3] == "sen":
        return "sen"
    else:
        print(fname)
        return "not found"


def createLegislatorsDict():
    """
    Creates our dictionary containing the information of all of the politicians

    :return: Dictionary containing a politician's name and chamber as the key and their term and
                full name information as the value, all grouped by the year
    """

    # reads in the json files containing the information of the politicians
    f = open("currentLegislators.json", "r")
    current = json.load(f)
    f.close()
    f = open("historicalLegislators.json", "r")
    historical = json.load(f)
    f.close()

    for year in current:  # loops through the years that we are concerned about for current
        for person in current[year]:  # loops through the politicians that were in congress during that year

            # puts current politicians into the same dictionary as retired politicians
            historical[year][person] = current[year][person]

    return historical


def hasNumbers(inputString):
    """
    Returns True if the string contains a number, False otherwise
    :param inputString: String to check for number
    :return: Boolean: whether string contains a number
    """
    return any(char.isdigit() for char in inputString)


def cleanContents(contents):
    """
    Cleans the contents of a file so that it no longer contains all the html tags and jargon

    :param contents: String containing the contents of a files
    :return: String of contents that no longer has html tags and jargon
    """

    # gets rid of anything that is not in the body
    bodystart = contents.index('<body>') + 6
    bodyend = contents.index('</body>')
    ret = contents[bodystart:bodyend]

    # gets rid of anything that is not in the pre
    if ret.index("<pre>") != -1:
        retstart = ret.index('<pre>') + 5
        retend = ret.index('</pre>')
        ret = ret[retstart:retend]
    return ret


def cleanForSpeeches(contents, year, writeToFile = False):
    """
    Cleans the ocngressional record to only contain speeches and returns a list of those speeches
    :param contents: String containing the text of the congressional record
    :param year: String containing the year that the speech was given
    :return: List containing only the speeches given in the file
    """

    recordList = []  # initializes the list of speeches that will be returned
    while True:
        speaker = findSpeaker(contents)  # returns the speaker of the next speech

        # potential spots where the next speaker started speech in record
        prefixes = [year+"\n", speaker]

        # the first spot where an element of prefixes occurs in contents
        spotToCheck = findFirstOcc(prefixes, contents, True)
        # breaks from the loop if there are no more speeches to be added to the recordList
        if spotToCheck == float('inf'):
            break

        else:
            # backgroundInfo = collectInfo(spotToCheck, contents) #gather speaker, state, chamber, and date

            contents = contents[spotToCheck:]  # trims everything before the next speech
            possibleEnds = ["____________________", findSpeaker(contents[3:])]  # potential spots where next speech ends
            endSpot = findFirstOcc(possibleEnds, contents[3:])  # returns where next speech ends or inf if it is EOF

            # reassings end of next speech to be the length of the contents if it is at the EOF
            if endSpot == float('inf'):
                endSpot = len(contents)

            # removes page numbers from contents
            pageLoc = contents.find("[[Page ")
            while pageLoc != -1:
                pageFinder = re.search('[[][[][P][a][g][e][ ].[0-9]+]]', contents)
                try:
                    page = pageFinder.group(0)
                except:
                    break
                contents = contents.replace(page, '')
                pageLoc = contents.find("[[Page ")

            # removes instances of "______________" from contents
            underscoreLoc = contents.find("______________")
            while underscoreLoc != -1:
                underscoreFinder = re.search('[_]+', contents)
                underscore = underscoreFinder.group(0)
                contents = contents.replace(underscore, '')
                underscoreLoc = contents.find("______________")

            # replaces instance of a double line break with a single line break
            lineBreakLoc = contents.find("\n\n")
            while lineBreakLoc != -1:
                contents = contents.replace("\n\n", "\n")
                lineBreakLoc = contents.find("\n\n")

            if contents[0:1] == 'M':  # checks for if it is a speaker or a formality
                if "[Roll No. " not in contents[:endSpot]:  # checks for if it is a speaker or a formality
                    recordList.append(contents[:endSpot])  # if actually a speech, append the speech to recordList

            contents = contents[endSpot:]  # update contents to not contain the speech we just added

    """if writeToFile:
        # write the speeches to a file named "writer.txt" with "\n\n\n" between each of the speeches
        writer = open("writer.txt", 'a')
        for r in recordList:
            for ch in r:
                writer.write(ch)
            writer.write("\n" + chamber + "\n" + year + "\n\n")
        writer.close()"""

    return recordList  # return a list of the speeches


def collectInfo(check, contents):
    """
    If the contents come from an extension of the congressional record,
    this function will collect the information of the speech's speaker

    :param check: int indicating the first spot to check for the speaker in contents
    :param contents: String containing the speech and the information of the speaker
    :return: List containing the information of the speaker, more specifically, the
                [name of the speaker, state of the speaker,
                    chamber that the speech was given in, date the speech was given]
    """

    # initializes all of the variables we want to return
    date = ""
    speaker = ""
    chamber = ""
    state = ""

    lines = 0  # maintains the number of lines we have parsed thus far. Only want to look at odd lines
    temp = 0  # maintains the end of the line we want to look at
    while check >= 0:

        # gathers the information that we want to return
        if contents[check] == "\n":  # only looks at new lines so that we only check lines where new information occurs
            lines += 1  # updates the number of lines we look at
            if lines % 2 == 0:  # accounts for the double line break between lines
                temp = check
            if lines == 3:
                date = contents[check:temp]  # assigns the date the speech was made
            if lines == 5:
                chamber = contents[check:temp].replace("in the ", "")  # assigns the chamber the speech was made in
            if lines == 7:
                state = contents[check:temp].replace("of ", "")  # assigns the state that the speaker is from
            if lines == 9:
                speaker = contents[check:temp].replace("HON. ", "")  # assigns the name of the speaker
                break
        check -= 1  # updates the location of that we want to check in contents

    return [speaker, state, chamber, date]  # returns an array of the information we want


def findSpeaker(contents):
    """
    takes in the congressional record and returns the speaker of the next speech

    :param contents: String containing the congressional record
    :return: String that is the name of the speaker of the next speech in contents (including their prefix)
                if more speeches in contents, otherwise returns "zzzzzzzzzzzzzzzzzzz"
    """

    speakerSearch = re.search('[M][r,s]{1,2}'r'. ''[A-Z]+[.]', contents)  # finds the next occurunce of a speaker
    try:
        speaker = speakerSearch.group(0)  # returns the name of the speaker of the next speech in contents
    except:
        speaker = "zzzzzzzzzzzzzzzzzzz"  # returns "zzzzzzzzzzzzzzzzzzz" if no new speech can be found in contents

    return speaker


def findFirstOcc(array, contents, startBool=False):
    """
    Finds the first occurunce in contents of any one of the elements in array and returns where that occurunce is
    :param array: List that we want to find where the first occurunce of any one of the elements in the list is
    :param contents: String that we want to find the first occurunce of an element of array in
    :param startBool: Boolean that indicates whether we want to include the prefix in the number that we return or not
    :return: int: where the first occurunce of an element in array occurs in contents
    """
    spotToCheck = float('inf')  # first occurunce thus far
    for prefix in array:  # iterates through the values that we want to check for
        temp = contents.find(prefix)  # finds the first occurunce of the prefix in contents

        """reassigns spotToCheck to be the first occurunce of an element of array in contents
        if it occurs before the previous spotToCheck"""
        if temp >= 0 and temp < spotToCheck:
            if startBool:
                if prefix == array[1]:
                    spotToCheck = temp
                else:
                    spotToCheck = temp + len(prefix) + 3
            else:
                spotToCheck = temp

    return spotToCheck


def findNth(haystack, needle, n):
    """
    Finds the location of the n-th occurunce of needle in haystack

    :param haystack: String that we want to parse for the n-th occurunce of needle
    :param needle: String that we want to find in haystack
    :param n: one more than the number of occurunces of needle we want to skip in haystack
    :return: int for the location of the n-th occurunce of needle in haystack, return -1 if not found
    """

    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


"""
def hasPhrase(phraseToCheck):
    phrasesCheckingFor = {"subsection", "sec", "act"}
    for word in phraseToCheck:
        if word in phrasesCheckingFor:
            return True
    return False
"""

main()
