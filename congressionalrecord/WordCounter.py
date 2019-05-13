import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import heapq


class WordCounter:
    words = []
    stopWords = set(stopwords.words('english'))
    newStopWords = ['congress', '', 'b', 'year', 'the', "'s", 'c', 'a', 'also', 'mr', 'ms', 'mrs', 'i', 'roll call',
                    'madam', "public law", "section", "act", "sec", "secretary state", "made available",
                    "united states", "remain available", "funds appropriated", "call roll", "new york",
                    "my time", "yield", "bill", "subsection", "sec", "act", "usc", "et", "seq", "committee",
                    "speaker", "dr", "hr", "today", "alabama", "alaska", "arizona", "srkansas", "california",
                    "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", "illinois",
                    "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
                    "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana",
                    "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
                    "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
                    "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah",
                    "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming", "gentleman",
                    "would", "north", "south", "may", "time", "house", "republican", "democrats", "president", "ask",
                    "dont", "thank", "make", "like", "ab", "pro", "pro tempore", "senate", "r", "congressman", "soon",
                    "met", "goes", "acts", "example", "fff", "bill", "act", "obama", 'v']
    ps = PorterStemmer()  # intiializes stemming object

    nonpartisanWordCounts = []  # maintains a count of all words said, regardless of party
    democratWordCounts = []  # maintains a count of all words said by Demcrats
    democratFrequencies = []  # stores the percentage of times a word is said by a Democrat
    republicanFrequencies = []  # stores the percentage of times a word is said by GOP

    # stores a count of every word and bigram said and whether it is used more by republicans or democrats
    wordsWoStopWords = []
    wordCounts = []

    def __init__(self):

        self.words = [self.wordCounts, self.wordsWoStopWords, self.democratWordCounts,
                      self.nonpartisanWordCounts, self.democratFrequencies, self.republicanFrequencies]

        for dic in self.words:
            for i in range(26):
                dic.append({})

        self.stopWords.update(self.newStopWords)  # updates stop words to include congressional stop words

    def addSingleWords(self, speech, speakerParty):
        sp = ""
        for w in speech.split(" "):

            checkPhrase = True  # boolean that checks to see if we should skip the phrase if it contains a stop word
            word = ""  # stores each word after removing non-alpha and non-space characters.
            for ch in w:  # removes non-alpha and non-space characters from words
                if ch.isalpha() or ch == " ":
                    word += ch.lower()
            if word not in self.stopWords:  # filters to remove stop words
                wordArr = word.split(" ")
                word = ""
                for wordToCheck in wordArr:
                    if wordToCheck not in self.stopWords:
                        stemmedWord = self.ps.stem(w)
                        word = stemmedWord + " "
                    else:
                        word = ""
                        checkPhrase = False

                if not checkPhrase:  # as long as the word is not in stopWords, keep going
                    continue

                if not hasNumbers(word):  # filters to remove numbers and words containing numbers, e.g.
                    wo = word
                    word = ""
                    for ch in wo:  # removes non-alpha and non-space characters from words
                        if ch.isalpha() or ch == " ":
                            word += ch.lower()

                    sp += word  # adds word to filtered speech

                    word = word.strip()
                    placeInArr = ord(word[0]) - ord('a')

                    if word not in self.wordsWoStopWords[placeInArr]:
                        # adds word to every dictionary of word counts if not in it
                        self.addWordToDicts(placeInArr, word)

        """ TODO: once resolving issue of politicians not being found in our database, can automatically call addBigrams
                from here instead of returning speech to fileIterator and calling addBigrams from there. When doing
                this, also try moving the for loop through speakerDict from fileIterator to this function in order to
                reduce the number of function calls you have to make across classes"""
        self.addBigrams(sp[:-1], speakerParty)  # removes extra space at end of speech and adds bigrams from speech

    def addBigrams(self, speech, speakerParty):
        bigrams = list(nltk.bigrams(speech.split()))  # creates a list of all bigrams in the filtered speech
        removeWordThreshold = 1 / 8
        for gram in bigrams:
            word = ""  # stores the bigram as a string
            skip = False  # if True, should skip the bigram because it contains a stop word
            for w in gram:
                if w in self.stopWords:
                    skip = True
                word += (w + " ")  # creates the bigram as a string
            if skip:
                continue  # does nothing with the bigram if it contains a stop word
            word = word[:-1]  # gets rid of the space on the end of the bigram string
            if not hasNumbers(word):  # skips the bigram if it contains a number
                if word not in self.stopWords:  # skips the bigram if it is in the stop words
                    placeInArr = ord(word[0]) - ord('a')

                    # adds the word to the dictionary containing a count of words with partisan association
                    if word not in self.wordsWoStopWords[placeInArr]:
                        # adds word to every dictionary of word counts if not in it
                        self.addWordToDicts(placeInArr, word)

                    #  adds count of words said to counts
                    self.addToCounts(placeInArr, word, speakerParty)

                    """if p percent of the time that a word occurs is within a bigram, we remove the individual word
                    from our word count dictionaries"""
                    for w in gram:
                        try:
                            bigramMentions = self.nonpartisanWordCounts[placeInArr][word]
                            singleWordMentions = self.nonpartisanWordCounts[placeInArr][w]
                            frequencyOfWord = bigramMentions / singleWordMentions
                            if frequencyOfWord > removeWordThreshold:
                                self.nonpartisanWordCounts[placeInArr].pop(w)
                                self.wordsWoStopWords[placeInArr].pop(w)
                                self.democratWordCounts[placeInArr].pop(w)
                        except:
                            pass

    def addWordToDicts(self, placeInArr, word):
        for d in range(len(self.words)):
            self.words[d][placeInArr][word] = 0

    def addToCounts(self, placeInArr, word, speakerParty):
        # increases count of word in non-partisan word count dict
        self.nonpartisanWordCounts[placeInArr][word] = self.nonpartisanWordCounts[placeInArr][word] + 1

        # increases count if dem said word the word
        if speakerParty == "democrat":
            self.wordsWoStopWords[placeInArr][word] = self.wordsWoStopWords[placeInArr][word] + 1
            self.democratWordCounts[placeInArr][word] = self.democratWordCounts[placeInArr][word] + 1

        # decreases count if gop said word the word
        elif speakerParty == "republican":
            self.wordsWoStopWords[placeInArr][word] = self.wordsWoStopWords[placeInArr][word] - 1

    def printTopFrequencies(self, wordCount, totalMentions, howMany, party):
        topWords = []  # heap of all of the words

        wordCountLen = 0

        for letter in range(len(wordCount)):
            wordCountLen += len(wordCount[letter])
            for w in wordCount[letter]:
                topWords.append((-wordCount[letter][w], w, -totalMentions[letter][w]))
                if len(topWords) > howMany:
                    maxLoc = topWords.index(max(topWords))
                    if maxLoc == len(topWords) - 1:
                        topWords.pop()
                    else:
                        topWords[maxLoc] = topWords.pop()

        print(wordCountLen)
        print(len(topWords))
        # prints the words that have the greatest magnitude of difference between times parties said word
        counter = 0
        stringToWrite = ""
        heapq.heapify(topWords)
        while counter < howMany:
            clause = heapq.heappop(topWords)
            counter += 1
            stringToWrite = (stringToWrite + str(clause[0])[1:4] + "           " + str(
                clause[1]) + "\n")  # + "        " + str(clause[2]) + "\n")
            if clause[0] > .5 and " " in clause[1]:
                print(clause[1])
        f = open(party + "Frequencies.txt", "w")
        f.write(stringToWrite)
        f.close()




def hasNumbers(inputString):
    """
    Returns True if the string contains a number, False otherwise
    :param inputString: String to check for number
    :return: Boolean: whether string contains a number
    """
    return any(char.isdigit() for char in inputString)

