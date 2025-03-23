"""
NLP
"""

import json
import random
from typing import Dict, List, Tuple, Optional

import spacy

MODEL_NAME = "en_core_web_md"
INTENTIONS_FILE = "chatbot/data/intentions.json"
SENTENCES_FILE = "chatbot/data/sentences.txt"


class NLP:
    """A class for processing natural language text using spaCy.

    This class provides natural language processing capabilities using spaCy's English
    language model. It handles model loading and provides methods for text analysis.
    """

    def __init__(self):
        """Initialize the NLP processor with spaCy's English language model."""
        try:
            self.__spacy = spacy.load(MODEL_NAME)
            self.__intentions = self._load_intentions(INTENTIONS_FILE)
            self.__sentences = self._load_sentences(SENTENCES_FILE)
        except OSError:
            # If model is not found, download it first
            spacy.cli.download(MODEL_NAME)
            self.__spacy = spacy.load(MODEL_NAME)

    def _load_intentions(self, file_path: str) -> Dict:
        """Load and parse the intentions JSON file.

        Args:
            file_path (str): Path to the intentions JSON file

        Returns:
            Dict: Parsed intentions data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_sentences(self, file_path: str) -> Dict[str, List[str]]:
        """Load and parse the sentences training file.

        Args:
            file_path (str): Path to the sentences file

        Returns:
            Dict[str, List[str]]: Dictionary mapping intents to example sentences
        """
        sentences = {}
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                intent, sentence = line.strip().split(" | ")
                if intent not in sentences:
                    sentences[intent] = []
                sentences[intent].append(sentence)
        return sentences

    def find_best_match(self, user_input: str) -> Tuple[Optional[str], float]:
        """Find the best matching intent for the user input.

        Args:
            user_input (str): User's input text

        Returns:
            Tuple[Optional[str], float]: Best matching intent and its confidence score
        """
        # First check basic intentions using pattern matching
        user_input_lower = user_input.lower()
        for intent, data in self.__intentions.items():
            if any(pattern in user_input_lower for pattern in data["patterns"]):
                return intent, 1.0

        # Then check sentence-based intents using NLP
        best_score = 0
        best_intent = None

        # Process user input
        user_doc = self.__spacy(user_input.lower())

        # Compare with each intent's sentences
        for intent, examples in self.__sentences.items():
            for example in examples:
                example_doc = self.__spacy(example.lower())
                similarity = user_doc.similarity(example_doc)

                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent

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
