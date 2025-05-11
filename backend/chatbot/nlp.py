"""
NLP
"""

import json
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from uuid import UUID
import spacy
from spacy.tokens import Doc

from spacy.matcher import Matcher

from .task1 import Task1
from .task3 import Task3
from engine import engine_response, ExpertaResponse
from .my_train_scrapper import MyTrainScrapper
from station import StationService
from api.managers import websocket_manager

MODEL_NAME = "en_core_web_md"
INTENTIONS_FILE = "chatbot/data/intentions.json"
SENTENCES_FILE = "chatbot/data/sentences.json"


class NLP:
    """A class for processing natural language text using spaCy.

    This class provides natural language processing capabilities using spaCy's English
    language model. It handles model loading and provides methods for text analysis.
    """

    def __init__(self, conversation_id: UUID):
        """Initialize the NLP processor with spaCy's English language model."""
        try:
            self.__spacy = spacy.load(MODEL_NAME)
        except OSError:
            # If model is not found, download it first
            spacy.cli.download(MODEL_NAME)
            self.__spacy = spacy.load(MODEL_NAME)
        self.__task1 = Task1()
        self.__task3 = Task3()
        self.__intentions = self._load_intentions(INTENTIONS_FILE)
        self.__sentences = self._load_sentences(SENTENCES_FILE)
        self.__experta = ExpertaResponse()
        self.__scrapper = MyTrainScrapper()
        self.__station_service = StationService()
        self.conversation_id = conversation_id

    def _load_intentions(self, file_path: str) -> Dict:
        """Load and parse the intentions JSON file.

        Args:
            file_path (str): Path to the intentions JSON file

        Returns:
            Dict: Parsed intentions data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_sentences(
        self, file_path: str
    ) -> tuple[Dict[str, Dict[str, List[str]]], Dict[str, List[Doc]]]:
        """Load and parse the sentences JSON file, also create spaCy docs for patterns.

        Args:
            file_path (str): Path to the sentences JSON file

        Returns:
            Dict[str, List[Doc]]:
                A tuple containing the pre-computed spaCy docs
        """
        with open(file_path, "r", encoding="utf-8") as f:
            sentences_data = json.load(f)

        # Pre-compute spaCy docs for all patterns
        sentences: Dict[str, List[Doc]] = {}

        for intent, data in sentences_data.items():
            sentences[intent] = []
            for example in data["patterns"]:
                example_doc: Doc = self.__spacy(example.lower())
                sentences[intent].append(example_doc)

        return sentences

    async def find_best_match(self, user_input: str) -> str:
        """Find the best matching intent for the user input.

        Args:
            user_input (str): User's input text

        Returns:
            Tuple[Optional[str], float]: Best matching intent and its confidence score
        """
        # First check basic intentions using pattern matching

        user_doc = self.__spacy(user_input.lower())
        matcher = Matcher(self.__spacy.vocab)

        # source_pattern = [{"LOWER": "source"}]

        greet_pattern = [{"LEMMA": {"IN": ["hey", "hello", "hi"]}}]

        thank_pattern = [
            {"LEMMA": {"IN": ["thank", "good", "wow", "great", "awesome"]}}
        ]

        bye_pattern = [{"LEMMA": {"IN": ["done", "nothing", "goodbye", "bye"]}}]

        find_pattern = [{"LEMMA": {"IN": ["train", "ticket", "book", "find", "look"]}}]

        travel_pattern = [{"LEMMA": {"IN": ["travel", "journey"]}}]

        station_pattern = [{"ENT_TYPE": "GPE"}, {"LOWER": "station"}]
        station_pattern_1 = [
            {"tag": "NNP"},
            {"tag": "NNP"},
            {"tag": "NN"},
            {"LOWER": "station"},
        ]
        station_pattern_2 = [{"tag": "NNP"}, {"tag": "NNP"}, {"LOWER": "station"}]

        source_pattern = [{"LOWER": "from"}]
        source_pattern_1 = [
            {"LEMMA": {"IN": ["source", "start", "begin", "origin", "board"]}}
        ]

        destination_pattern_2 = [{"LOWER": "to"}]
        # destination_pattern = [{"LOWER": "destination"}]
        destination_pattern = [
            {"LEMMA": {"IN": ["destination", "end", "final", "stop", "deboard"]}}
        ]

        date_pattern = [{"ENT_TYPE": "DATE"}, {"ENT_TYPE": "DATE"}]
        time_pattern = [{"ENT_TYPE": "TIME"}]
        time_pattern_1 = [{"ENT_TYPE": "TIME"}, {"ENT_TYPE": "TIME"}]

        delay_pattern = [{"LEMMA": {"IN": ["delay", "late"]}}]

        incident_pattern = [{"LEMMA": {"IN": ["incident", "issue", "problem"]}}]
        location_pattern = [
            {"LEMMA": {"IN": ["location", "between", "occur", "happen"]}}
        ]
        location_pattern_1 = [
            {"ENT_TYPE": "GPE"},
            {"LOWER": "between"},
            {"ENT_TYPE": "GPE"},
        ]

        blockage_pattern = [{"LEMMA": {"IN": ["partial", "full"]}}]
        weather_pattern = [
            {
                "LEMMA": {
                    "IN": [
                        "high winds",
                        "wind",
                        "flood",
                        "snow",
                        "frost",
                        "autumn",
                        "high temperature",
                    ]
                }
            }
        ]

        matcher.add("greet", [greet_pattern])
        matcher.add("thank", [thank_pattern])
        matcher.add("bye", [bye_pattern])
        matcher.add("find", [find_pattern])
        matcher.add("travel", [travel_pattern])
        matcher.add("station", [station_pattern, station_pattern_1, station_pattern_2])
        matcher.add("source", [source_pattern, source_pattern_1])
        matcher.add("destination", [destination_pattern, destination_pattern_2])
        matcher.add("date", [date_pattern])
        matcher.add("time", [time_pattern, time_pattern_1])
        matcher.add("delay", [delay_pattern])
        matcher.add("incident", [incident_pattern])
        matcher.add("location", [location_pattern, location_pattern_1])
        matcher.add("blockage", [blockage_pattern])
        matcher.add("blockage_time", [time_pattern, time_pattern_1])
        matcher.add("weather", [weather_pattern])

        #
        # lemmatized_input = ''
        #
        # for token in user_doc:
        #     lemmatized_input += token.lemma_ + ' '
        #
        # print('LEMMA',lemmatized_input)

        matches = matcher(user_doc)
        for match_id, start, end in matches:
            string_id = self.__spacy.vocab.strings[match_id]
            span = user_doc[start:end]
            print("Match", match_id, span.text, string_id)

            if (
                string_id == "find"
                or string_id == "thank"
                or string_id == "bye"
                or string_id == "greet"
                or string_id == "delay"
                or string_id == "travel"
                or string_id == "incident"
            ):
                engine_response(string_id)

            if string_id == "date":
                self.__task1.set_date_of_travel(span.text)
                # engine_response(string_id.lower())
                if self.__task1.get_time_of_travel() is None:
                    engine_response("time")
                else:
                    self.check_task1_missing_info()

            if string_id == "time":
                time = ""
                for token in user_doc:
                    if token.ent_type_ == "TIME":
                        print(token.text)
                        time += token.text + " "

                self.__task1.set_time_of_travel(time)

                if self.__task1.get_date_of_travel() is None:
                    engine_response("date")
                else:
                    self.check_task1_missing_info()

            if string_id == "source":
                source_name = ""
                for token in user_doc:
                    if token.lemma_ == "to":
                        break
                    if token.ent_type_ == "GPE" or token.tag_ in ["NNP", "NNPS", "NNS"]:

                        source_name += token.text.capitalize() + " "
                        # break

                self.__task1.set_source_station(source_name)
                engine_response("source")

            if string_id == "destination":
                destination_name = ""
                for token in user_doc:
                    if token.lemma_ == "to":
                        destination_name = ""
                    if token.ent_type_ == "GPE" or token.tag_ in ["NNP", "NNPS", "NNS"]:

                        destination_name += token.text.capitalize() + " "

                self.__task1.set_destination_station(destination_name)
                engine_response("destination")

            if string_id == "location":
                location = []
                for token in user_doc:
                    print(token.text, token.tag_)
                    if token.tag_ == "NNP" or token.tag_ == "NN":
                        location.append(token.text)

                    if token.tag_ == "TIME":
                        self.__task3.set_time_of_incident(token.text)

                self.__task3.set_location_one(location[0])
                self.__task3.set_location_two(location[1])
                engine_response("location")

            if string_id == "blockage":
                self.__task3.set_type_of_blockage(span.text)
                engine_response(
                    "line_contingency-"
                    + self.__task3.get_location_one()
                    + "-"
                    + self.__task3.get_location_two()
                    + "-"
                    + self.__task3.get_type_of_blockage()
                )

            if string_id == "weather":
                print(span.text)
                if span.text[-1:] == "s":
                    engine_response("weather_contingency-" + span.text[0:-1])
                else:
                    engine_response("weather_contingency-" + span.text)

        if len(matches) == 0:
            engine_response(user_input.lower())

        print("TASK 1 INFO ")
        print(self.__task1.get_time_of_travel())
        print(self.__task1.get_date_of_travel())
        print(self.__task1.get_source_station())
        print(self.__task1.get_destination_station())

        print("TASK 3 INFO")
        print(self.__task3.get_type_of_blockage())
        print(self.__task3.get_time_of_incident())
        print(self.__task3.get_location_one())
        print(self.__task3.get_location_two())

        if self.__task1.check_all_details_gathered():


            await websocket_manager.send_message(self.conversation_id, "Hey hey this is Vanya")
            source_station = self.__station_service.search_by_name(
                self.__task1.get_source_station().strip()
            )
            print(source_station)

            dest_station = self.__station_service.search_by_name(
                self.__task1.get_destination_station().strip()
            )
            print(dest_station)

            date_string = (
                self.__task1.get_date_of_travel().capitalize()
                + ", 2025 "
                + self.__task1.get_time_of_travel().upper()
            )
            print(date_string)
            date_format = "%B %d, %Y %I:%M %p"
            datetime_object = datetime.strptime(date_string.strip(), date_format)
            # print(datetime_object)
            formatted_date_string = datetime_object.strftime("%Y-%m-%dT%H:%M:%SZ")
            # print(formatted_date_string)
            url = ""
            if len(source_station) == 0 or len(dest_station) == 0:

                engine_response("sorry_no_station")

            else:
                url = self.__scrapper.run_scrapper(
                    source_station[0].my_train_code,
                    dest_station[0].my_train_code,
                    formatted_date_string,
                )
                # print(url)
            self.__task1.remove_all_info()
            if url == "":
                engine_response("sorry_task1")
                return self.__experta.get_engine_response()
            return url

        # engine_response('contingency-colchester-manningtree-partial')
        # user_input_lower = user_input.lower()
        # for intent, data in self.__intentions.items():
        #     if any(pattern in user_input_lower for pattern in data["patterns"]):
        #         return intent, 1.0

        # # Then check sentence-based intents using NLP
        # best_score = 0
        # best_intent = None

        # user_doc = self.__spacy(user_input.lower())

        # # Compare with each pre-computed example doc
        # for intent, example_docs in self.__sentences.items():
        #     for example_doc in example_docs:
        #         similarity = user_doc.similarity(example_doc)

        #         if similarity > best_score:
        #             best_score = similarity
        #             best_intent = intent

        # print("best score:", best_score)

        # return best_intent, best_score

        return self.__experta.get_engine_response()

    def process_basic_intentions(self, intent: str) -> str:
        """
        Process basic intentions from JSON.

        Args:
            intent (str): Intent to process

        Returns:
            str: Response from the processed intent
        """

        if intent in self.__intentions:
            return random.choice(self.__intentions[intent]["responses"])

        return "I'm not sure how to respond to that."

    def check_task1_missing_info(self):

        task_1_collected = self.__task1.check_what_info_missing()
        if task_1_collected is None:
            engine_response("got_all")
        else:
            engine_response(task_1_collected)
