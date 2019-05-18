import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import heapq
from IndividualWordCounter import IndividualWordCounter as IWC


class WordCounter:
    words = []  # array that has pointers to all of the different word count dictionaries
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

    counter1 = 0
    counter2 = 0  # two counters to help keep track of how many words are stored

    """
    nonpartisanWordCounts = IWC("nonpartisanWordCounts")  # maintains a count of all words said, regardless of party
    democratWordCounts = IWC("democratWordCounts")  # maintains a count of all words said by Demcrats
    democratFrequencies = IWC("democratFrequencies")  # stores the percentage of times a word is said by a Democrat
    republicanFrequencies = ["republicanFrequencies"]  # stores the percentage of times a word is said by GOP
    """

    # stores a count of every word and bigram said and whether it is used more by republicans or democrats
    wordsWoStopWords = []
    wordCounts = []

    def __init__(self):

        # initializes words array
        self.words = [self.wordCounts, self.wordsWoStopWords, self.democratWordCounts,
                      self.nonpartisanWordCounts, self.democratFrequencies, self.republicanFrequencies]

        # initializes each word count dictionary
        for dic in self.words:
            for i in range(26):
                dic.append([])  # adds 26 arrays, one for each letter that a word could start with
        for dic in self.words:
            for let in dic:
                for i in range(26):
                    let.append({})  # adds 26 arrays to each subarray. One for each possible second letter in a word

        self.stopWords.update(self.newStopWords)  # updates stop words to include congressional stop words

    def addSingleWords(self, speech, speakerParty):
        sp = ""
        for w in speech.split(" "):

            checkPhrase = True  # boolean that checks to see if we should skip the phrase if it contains a stop word
            word = ""  # stores each word after removing non-alpha and non-space characters.
            for ch in w:  # removes non-alpha and non-space characters from words
                if ch.isalpha() or ch == " ":
                    word += ch.lower()
            if word not in self.stopWords:  # entire conditional statement filters to remove stop words
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
                    word = word.strip()  # removes space from end of word

                    firstLetter = ord(word[0]) - ord('a')  # stores the position in the alphabet of the first letter
                    try:
                        secLetter = ord(word[1]) - ord('a')  # stores the position in the alphabet of the second letter
                    except:
                        secLetter = 25  # starts with 'z' otherwise
                    placeInArr = (firstLetter, secLetter)  # stores the first and second letters in the word

                    if word not in self.wordsWoStopWords[firstLetter][secLetter]:
                        # adds word to every dictionary of word counts if not in it
                        self.addWordToDicts(placeInArr, word)

                        # can delete once done
                        if self.counter1 >= 2000000:
                            self.counter1 = 0
                            self.counter2 += 1
                        self.counter1 += 1
                        print(str(self.counter1) + "    " + str(self.counter2))

                    self.addToCounts(placeInArr, word, speakerParty)  # adds count of words said to counts

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
                    firstLetter = ord(word[0]) - ord('a')  # stores the position in the alphabet of the first letter

                    # stores the position in the alphabet of the second letter
                    if word[1] == " ":
                        secLetter = ord(word[2]) - ord('a')
                    else:
                        secLetter = ord(word[1]) - ord('a')

                    placeInArr = (firstLetter, secLetter)  # stores the first and second letters in the word

                    # adds the word to the dictionary containing a count of words with partisan association
                    if word not in self.wordsWoStopWords[firstLetter][secLetter]:
                        # adds word to every dictionary of word counts if not in it
                        self.addWordToDicts(placeInArr, word)

                        # can delete once working
                        if self.counter1 >= 2000000:
                            self.counter1 = 0
                            self.counter2 += 1
                        self.counter1 += 1
                        print(str(self.counter1) + "    " + str(self.counter2))

                    self.addToCounts(placeInArr, word, speakerParty)  # adds count of words said to counts

                    """if p percent of the time that a word occurs is within a bigram, we remove the individual word
                    from our word count dictionaries"""
                    for w in gram:
                        try:
                            bigramMentions = self.nonpartisanWordCounts[firstLetter][secLetter][word]
                            singleWordMentions = self.nonpartisanWordCounts[firstLetter][secLetter][w]
                            frequencyOfWord = bigramMentions / singleWordMentions
                            if frequencyOfWord > removeWordThreshold:
                                self.nonpartisanWordCounts[firstLetter][secLetter].pop(w)
                                self.wordsWoStopWords[firstLetter][secLetter].pop(w)
                                self.democratWordCounts[firstLetter][secLetter].pop(w)
                        except:
                            pass

    def calculateFrequencies(self, minimumOccs):
        """
        Calculates the frequencies in which phrases are said by either party

        :param minimumOccs: The minimum number of times a word must occur in order for us to calculate its partisanship
        :return: None
        """

        for firstLetter in range(len(self.nonpartisanWordCounts)):  # iterates through starting letters
            for secLetter in range(len(self.nonpartisanWordCounts[firstLetter])):  # iterates through second letters
                for word in self.nonpartisanWordCounts[firstLetter][secLetter]:  # iterates through all words

                    # stores all times the word is said regardless of party
                    totalMentions = self.nonpartisanWordCounts[firstLetter][secLetter][word]

                    if totalMentions >= minimumOccs:  # makes sure word is said minimum number of times
                        democratMentions = self.democratWordCounts[firstLetter][secLetter][word]  # stores dem mentions
                        republicanMentions = totalMentions - democratMentions  # stores gop mentions
                        self.democratFrequencies[firstLetter][secLetter][word] = democratMentions / totalMentions
                        self.republicanFrequencies[firstLetter][secLetter][word] = republicanMentions / totalMentions

    def addWordToDicts(self, placeInArr, word):
        """
        Adds a word or phrase to all of the word count arrays

        :param placeInArr: tuple indicating where to store the word in the array. Tuple is (first letter, second letter)
        :param word: phrase that is being added to array
        :return: None
        """

        firstLetter = placeInArr[0]  # location in alphabet of starting letter
        secLetter = placeInArr[1]  # locaiton in alphabet of second letter
        for d in range(len(self.words)):  # iterates through all word count arrays
            self.words[d][firstLetter][secLetter][word] = 0  # initializes word in the correct location

    def addToCounts(self, placeInArr, word, speakerParty):
        """
        Correctly updates the count of the word said in all word count arrays for each mention of a word

        :param placeInArr: tuple indicating where to store the word in the array. Tuple is (first letter, second letter)
        :param word: phrase that is being added to array
        :param speakerParty: party of the person who said the word on this occurrence
        :return:
        """

        firstLetter = placeInArr[0]
        secLetter = placeInArr[1]

        # increases count of word in non-partisan word count dict
        self.nonpartisanWordCounts[firstLetter][secLetter][word] = \
            self.nonpartisanWordCounts[firstLetter][secLetter][word] + 1

        # increases count if dem said word the word
        if speakerParty == "democrat":
            self.wordsWoStopWords[firstLetter][secLetter][word] = \
                self.wordsWoStopWords[firstLetter][secLetter][word] + 1

            self.democratWordCounts[firstLetter][secLetter][word] = \
                self.democratWordCounts[firstLetter][secLetter][word] + 1

        # decreases count if gop said word the word
        elif speakerParty == "republican":
            self.wordsWoStopWords[firstLetter][secLetter][word] = \
                self.wordsWoStopWords[firstLetter][secLetter][word] - 1

    def printTopFrequencies(self, howMany=1000, whichParty='gop'):
        """
        Prints the words that have the highest partisan lean

        :param howMany: How many words to print
        :param whichParty: The party whose highly partisan words are to be printed (either 'dem' or 'gop')
        :return: None
        """

        topWords = []  # heap of all of the words

        # determines which wordCount to print
        if whichParty.lower() == "dem":
            wordCount = self.democratFrequencies
        elif whichParty.lower() == "gop" or whichParty.lower() == "rep":
            wordCount = self.republicanFrequencies
        else:
            raise Exception("Must specify party as either \"dem\" or \"gop\"")

        wordCountLen = 0  # keeps track of how many words are being said

        for firstLetter in range(len(wordCount)):  # iterates through starting letters
            for secLetter in range(len(wordCount[firstLetter])):  # iterates through second letters
                wordCountLen += len(wordCount[firstLetter][secLetter])  # maintains count of how many phrases are said
                for w in wordCount[firstLetter][secLetter]:  # iterates through phrases said
                    topWords.append((-wordCount[firstLetter][secLetter][w], w))  # adds the latest word to the heap

                    # if the heap exceeds the number of words we want to return, then remove the lowest partisan word
                    if len(topWords) > howMany:
                        maxLoc = topWords.index(max(topWords))
                        if maxLoc == len(topWords) - 1:
                            topWords.pop()
                        else:
                            topWords[maxLoc] = topWords.pop()

        print(wordCountLen)  # counts how many words total were considered
        print(len(topWords))  # makes sure the heap never exceeded a size of howMany + 1

        # prints the words that have the greatest partisan lean and writes them to a text file
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
        f = open(whichParty + "ClassFrequencies.txt", "w")
        f.write(stringToWrite)
        f.close()


def hasNumbers(inputString):
    """
    Returns True if the string contains a number, False otherwise
    :param inputString: String to check for number
    :return: Boolean: whether string contains a number
    """
    return any(char.isdigit() for char in inputString)
