class IndividualWordCounter:
    name = ""
    data = []

    def __init__(self, name):
        self.name = name
        for i in range(26):
            self.data.append({})