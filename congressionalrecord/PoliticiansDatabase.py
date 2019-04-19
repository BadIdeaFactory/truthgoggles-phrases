import json

class PoliticiansDatabase:
    legislators = {}

    def __init__(self):
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

        writer = open("legislator.json", 'w')
        json.dump(historical, writer)
        writer.close()

        self.legislators = historical

    def getSpeakerParty(self, year, speakerDictKey):
        try:
            return self.legislators[year][speakerDictKey]['terms']['party'].lower()
        except:
            return "not found"

    def yearOfLegislators(self, year):
        if year not in self.legislators.keys():
            raise ValueError('Tried to get a year of politicians that does not exist. ')

        return self.legislators[year]
