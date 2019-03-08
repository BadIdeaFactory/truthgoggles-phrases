"""

"""

def parsePol(pol):
    name = pol["name"]["official_full"]
    lastName = pol["name"]["last"]
    terms = pol["terms"]
    for term in range(terms):
        chamber = term["type"]
        #startYear =
    """
    {"name": {"first": "Tom", "last": "Graves", "official_full": "Tom Graves"}, "terms": [{"end": "2011-01-03", "party": "Republican", "url": "http://tomgraves.house.gov/", "district": 9, "state": "GA", "type": "rep", "start": "2010-06-08"}, {"contact_form": "http://tomgraves.house.gov/contact/", "district": 9, "party": "Republican", "end": "2013-01-03", "fax": "202-225-8272", "office": "1113 Longworth House Office Building", "url": "http://tomgraves.house.gov/", "phone": "202-225-5211", "state": "GA", "address": "1113 Longworth HOB; Washington DC 20515-1010", "type": "rep", "start": "2011-01-05"}, {"contact_form": "http://tomgraves.house.gov/contact/", "district": 14, "type": "rep", "end": "2015-01-03", "fax": "202-225-8272", "office": "432 Cannon House Office Building", "url": "http://tomgraves.house.gov", "phone": "202-225-5211", "state": "GA", "address": "432 Cannon HOB; Washington DC 20515-1014", "party": "Republican", "rss_url": "http://tomgraves.house.gov/news/rss.aspx", "start": "2013-01-03"}, {"contact_form": "http://tomgraves.house.gov/contact/", "district": 14, "type": "rep", "end": "2017-01-03", "fax": "202-225-8272", "office": "2442 Rayburn House Office Building", "url": "http://tomgraves.house.gov", "phone": "202-225-5211", "state": "GA", "address": "2442 Rayburn HOB; Washington DC 20515-1014", "party": "Republican", "rss_url": "http://tomgraves.house.gov/news/rss.aspx", "start": "2015-01-06"}, {"fax": "202-225-8272", "rss_url": "http://tomgraves.house.gov/news/rss.aspx", "party": "Republican", "end": "2019-01-03", "district": 14, "office": "2078 Rayburn House Office Building", "url": "https://tomgraves.house.gov", "phone": "202-225-5211", "state": "GA", "address": "2078 Rayburn House Office Building; Washington DC 20515-1014", "type": "rep", "start": "2017-01-03"}, {"end": "2021-01-03", "rss_url": "http://tomgraves.house.gov/news/rss.aspx", "party": "Republican", "office": "2078 Rayburn House Office Building", "url": "https://tomgraves.house.gov", "phone": "202-225-5211", "district": 14, "state": "GA", "address": "2078 Rayburn House Office Building; Washington DC 20515-1014", "type": "rep", "start": "2019-01-03"}]}
    """

class Politician:
    name = ""
    state = ""
    party = ""
    chamber = ""
    repYears = ("", "")
    senYears = ("", "")

    def __init__(self, name, state, party, chamber, terms):
        self.name = name
        self.state = state
        self.party = party
        self.chamber = chamber
        repYears = ("0", "0")
        senYears = ("0", "0")
        for term in terms:
            whereAt = term[0]["type"]

        self.repYears = repYears
        self.senYears = senYears

