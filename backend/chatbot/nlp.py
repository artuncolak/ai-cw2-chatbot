"""
NLP
"""

import json
import random
from typing import Dict, List, Tuple, Optional

import spacy
from spacy.tokens import Doc

from spacy.matcher import Matcher

from .task1 import Task1

MODEL_NAME = "en_core_web_md"
INTENTIONS_FILE = "chatbot/data/intentions.json"
SENTENCES_FILE = "chatbot/data/sentences.json"


class NLP:
    """A class for processing natural language text using spaCy.

    This class provides natural language processing capabilities using spaCy's English
    language model. It handles model loading and provides methods for text analysis.
    """

    def __init__(self):
        """Initialize the NLP processor with spaCy's English language model."""
        try:
            self.__spacy = spacy.load(MODEL_NAME)
        except OSError:
            # If model is not found, download it first
            spacy.cli.download(MODEL_NAME)
            self.__spacy = spacy.load(MODEL_NAME)
        self.__task1 = Task1()
        self.__intentions = self._load_intentions(INTENTIONS_FILE)
        self.__sentences = self._load_sentences(SENTENCES_FILE)

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

    def find_best_match(self, user_input: str) -> Tuple[Optional[str], float]:
        """Find the best matching intent for the user input.

        Args:
            user_input (str): User's input text

        Returns:
            Tuple[Optional[str], float]: Best matching intent and its confidence score
        """
        # First check basic intentions using pattern matching


        user_doc = self.__spacy(user_input.lower())
        matcher = Matcher(self.__spacy.vocab)
        source_pattern = [{"LOWER": "source"}]
        destination_pattern = [{"LOWER": "destination"}]
        date_pattern = [{"ENT_TYPE": "DATE"},{"ENT_TYPE": "DATE"}]
        time_pattern = [{"ENT_TYPE": "TIME"}]

        matcher.add('source',[source_pattern])
        matcher.add('destination',[destination_pattern])
        matcher.add("date", [date_pattern])
        matcher.add("time", [time_pattern])

        matches = matcher(user_doc)
        for match_id, start, end in matches:
            string_id = self.__spacy.vocab.strings[match_id]
            span  = user_doc[start:end]
            print("Match", match_id, span.text, string_id)

            if string_id == "date":
                self.__task1.set_date_of_travel(span.text)

            if string_id == "time":
                self.__task1.set_time_of_travel(span.text)

            if string_id == "source":
                for token in user_doc:
                    if token.ent_type_ == "GPE":
                        self.__task1.set_source_station(token.text)

            if string_id == "destination":
                for token in user_doc:
                    if token.ent_type_ == "GPE":
                        self.__task1.set_destination_station(token.text)


        print(self.__task1.get_time_of_travel())
        print(self.__task1.get_date_of_travel())
        print(self.__task1.get_source_station())
        print(self.__task1.get_destination_station())

        user_input_lower = user_input.lower()
        for intent, data in self.__intentions.items():
            if any(pattern in user_input_lower for pattern in data["patterns"]):
                return intent, 1.0

        # Then check sentence-based intents using NLP
        best_score = 0
        best_intent = None

        user_doc = self.__spacy(user_input.lower())

        # Compare with each pre-computed example doc
        for intent, example_docs in self.__sentences.items():
            for example_doc in example_docs:
                similarity = user_doc.similarity(example_doc)

                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent

        print("best score:", best_score)

        return best_intent, best_score



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
