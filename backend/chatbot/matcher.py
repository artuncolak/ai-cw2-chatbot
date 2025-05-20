import spacy
from spacy.tokens import Doc

from spacy.matcher import Matcher
MODEL_NAME = "en_core_web_md"

class SpacyMatcher:

    def __init__(self):
        try:
            self.__spacy = spacy.load(MODEL_NAME)
        except OSError:
            # If model is not found, download it first
            spacy.cli.download(MODEL_NAME)
            self.__spacy = spacy.load(MODEL_NAME)

        self.matcher = Matcher(self.__spacy.vocab)

        self.greet_pattern = [{"LEMMA": {"IN": ["hey", "hello", "hi"]}}]

        self.cancel_pattern = [{"LEMMA": {"IN": ["cancel", "abort", "reset","no"]}}]

        self.thank_pattern = [
            {"LEMMA": {"IN": ["thank", "good", "wow", "great", "awesome"]}}
        ]

        self.bye_pattern = [{"LEMMA": {"IN": ["done", "nothing", "goodbye", "bye"]}}]

        self.find_pattern = [{"LEMMA": {"IN": ["train", "ticket", "book", "find", "look"]}}]

        self.travel_pattern = [{"LEMMA": {"IN": ["travel", "journey"]}}]

        self.station_pattern = [{"ENT_TYPE": "GPE"}, {"LOWER": "station"}]
        self.station_pattern_1 = [
            {"tag": "NNP"},
            {"tag": "NNP"},
            {"tag": "NN"},
            {"LOWER": "station"},
        ]
        self.station_pattern_2 = [{"tag": "NNP"}, {"tag": "NNP"}, {"LOWER": "station"}]
        self.station_pattern_3 = [{"TEXT": {"FUZZY": "station"}}]


        self.source_pattern = [{"LOWER": "from"}, {"tag": {"IN": ["NNP", "NNPS", "NNS"]}}]
        self.source_pattern_1 = [
            {"LEMMA": {"IN": ["source", "start", "begin", "origin", "board"]}}
        ]
        self.source_pattern_3 = [{"TEXT": {"FUZZY": "source"}}]


        self.destination_pattern_2 = [{"LOWER": "to"}, {"tag": {"IN": ["NNP", "NNPS", "NNS"]}}]
        # destination_pattern = [{"LOWER": "destination"}]
        self.destination_pattern = [
            {"LEMMA": {"IN": ["destination", "end", "final", "stop", "deboard"]}}
        ]
        self.destination_pattern_3 = [{"TEXT": {"FUZZY": "destination"}}]


        self.date_pattern = [{"ENT_TYPE": "DATE"}, {"ENT_TYPE": "DATE"}]
        self.time_pattern = [{"ENT_TYPE": "TIME"}]
        self.time_pattern_1 = [{"ENT_TYPE": "TIME"}, {"ENT_TYPE": "TIME"}]

        self.delay_pattern = [{"LEMMA": {"IN": ["delay", "late"]}}]

        self.incident_pattern = [{"LEMMA": {"IN": ["incident", "issue", "problem"]}}]
        self.location_pattern = [
            {"LEMMA": {"IN": ["location", "between", "occur", "happen"]}}
        ]
        self.location_pattern_1 = [
            {"ENT_TYPE": "GPE"},
            {"LOWER": "between"},
            {"ENT_TYPE": "GPE"},
        ]

        self.blockage_pattern = [{"LEMMA": {"IN": ["partial", "full"]}}]
        # self.blockage_pattern_1 = [{"TEXT": {"FUZZY": "partial"}}]

        self.weather_pattern = [
            {
                "LEMMA": {
                    "IN": [
                        "high winds",
                        "wind",
                        "flood",
                        "snow",
                        "frost",
                        "autumn",
                        "high temperatures",
                        "high temperature"
                        "temperature"
                    ]
                }
            }
        ]

        self.confirm_pattern = [{"LEMMA": {"IN": ["yes", "confirm"]}}]

        self.matcher.add("greet", [self.greet_pattern])
        self.matcher.add("cancel", [self.cancel_pattern])
        self.matcher.add("thank", [self.thank_pattern])
        self.matcher.add("bye", [self.bye_pattern])
        self.matcher.add("find", [self.find_pattern])
        self.matcher.add("travel", [self.travel_pattern])
        self.matcher.add("station", [self.station_pattern, self.station_pattern_1, self.station_pattern_2, self.station_pattern_3])
        self.matcher.add("source", [self.source_pattern, self.source_pattern_1, self.source_pattern_3])
        self.matcher.add("destination", [self.destination_pattern, self.destination_pattern_2, self.destination_pattern_3])
        self.matcher.add("date", [self.date_pattern])
        self.matcher.add("time", [self.time_pattern, self.time_pattern_1])
        self.matcher.add("delay", [self.delay_pattern])
        self.matcher.add("incident", [self.incident_pattern])
        self.matcher.add("location", [self.location_pattern, self.location_pattern_1])
        self.matcher.add("blockage", [self.blockage_pattern])
        self.matcher.add("blockage_time", [self.time_pattern, self.time_pattern_1])
        self.matcher.add("weather", [self.weather_pattern])
        self.matcher.add("confirm", [self.confirm_pattern])

        self.user_doc = None

    def get_spacy(self):
        return self.__spacy

    def set_user_doc(self, user_input):
        self.user_doc = self.__spacy(user_input)

    def get_user_doc(self):
        return self.user_doc

    def perform_matching(self, user_input):
        user_doc = self.__spacy(user_input)
        return self.matcher(user_doc)

    # def give_user_doc(self, user_input):
    #     return self.__spacy(user_input)

