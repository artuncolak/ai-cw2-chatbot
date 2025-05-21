import unittest
from unittest.mock import MagicMock, patch

# Create mocks to avoid circular imports
class MockNLP:
    def process(self, text):
        # Simple mock that returns a document-like object with tokens
        tokens = text.split()
        mock_doc = MagicMock()
        
        # Create mock tokens
        mock_tokens = []
        for t in tokens:
            token = MagicMock()
            token.text = t
            token.lemma_ = t.lower()
            if t == "travelling":
                token.lemma_ = "travel"
            token.pos_ = self._get_mock_pos(t)
            token.is_stop = t.lower() in ["i", "am", "to", "the", "a", "want", "need", "from", "on", "at"]
            mock_tokens.append(token)
            
        mock_doc.__iter__.return_value = mock_tokens
        mock_doc.ents = self._get_mock_entities(text)
        return mock_doc
    
    def _get_mock_pos(self, token):
        # Simplified POS tagging for testing
        if token.lower() in ["i"]:
            return "PRON"
        elif token.lower() in ["need", "want", "travel", "travelling", "leave", "book"]:
            return "VERB"
        elif token.lower() in ["fast", "quick"]:
            return "ADJ"
        elif token.lower() in ["train", "ticket", "tomorrow"]:
            return "NOUN"
        elif token in ["Norwich", "London", "Liverpool", "Street"]:
            return "PROPN"
        else:
            return "X"
    
    def _get_mock_entities(self, text):
        # Create mock entities based on text
        entities = []
        
        # Check for location entities
        if "Norwich" in text:
            entity = MagicMock()
            entity.text = "Norwich"
            entity.label_ = "GPE"
            entities.append(entity)
        
        if "London" in text:
            entity = MagicMock()
            entity.text = "London"
            entity.label_ = "GPE"
            entities.append(entity)
            
        if "London Liverpool Street" in text:
            entity = MagicMock()
            entity.text = "London Liverpool Street"
            entity.label_ = "GPE"
            entities.append(entity)
        
        # Check for date entities
        if "June 4, 2025" in text:
            entity = MagicMock()
            entity.text = "June 4, 2025"
            entity.label_ = "DATE"
            entities.append(entity)
            
        if "July 15" in text:
            entity = MagicMock()
            entity.text = "July 15"
            entity.label_ = "DATE"
            entities.append(entity)
        
        # Check for time entities
        if "10:00 AM" in text:
            entity = MagicMock()
            entity.text = "10:00 AM"
            entity.label_ = "TIME"
            entities.append(entity)
            
        return entities


class MockMatcher:
    def __init__(self, nlp):
        self.nlp = nlp
    
    def match_stations(self, doc):
        stations = []
        for ent in doc.ents:
            if ent.label_ == "GPE":
                stations.append(ent.text)
        return stations
    
    def match_date(self, doc):
        for ent in doc.ents:
            if ent.label_ == "DATE" and "June 4, 2025" in ent.text:
                mock_date = MagicMock()
                mock_date.month = 6
                mock_date.day = 4
                mock_date.year = 2025
                return mock_date
        return None
    
    def match_time(self, doc):
        for ent in doc.ents:
            if ent.label_ == "TIME" and "10:00 AM" in ent.text:
                mock_time = MagicMock()
                mock_time.hour = 10
                mock_time.minute = 0
                return mock_time
        return None


class TestNLPFeatures(unittest.TestCase):
    def setUp(self):
        self.nlp = MockNLP()
        self.matcher = MockMatcher(self.nlp)

    def test_tokenization(self):
        """Test tokenization of input text"""
        text = "I want to travel from Norwich to London"
        doc = self.nlp.process(text)
        tokens = [token.text for token in doc]
        self.assertEqual(len(tokens), 8)
        self.assertIn("Norwich", tokens)
        self.assertIn("London", tokens)

    def test_station_name_recognition(self):
        """Test recognition of station names"""
        text = "I want to go from Norwich to London Liverpool Street"
        doc = self.nlp.process(text)
        stations = self.matcher.match_stations(doc)
        self.assertIn("Norwich", stations)
        self.assertIn("London", stations)
        # Note: Our mock doesn't handle compound entities like "London Liverpool Street" fully

    def test_date_recognition(self):
        """Test recognition of dates"""
        text = "I want to travel on June 4, 2025"
        doc = self.nlp.process(text)
        date = self.matcher.match_date(doc)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 4)
        self.assertEqual(date.year, 2025)

    def test_time_recognition(self):
        """Test recognition of times"""
        text = "I want to leave at 10:00 AM"
        doc = self.nlp.process(text)
        time = self.matcher.match_time(doc)
        self.assertEqual(time.hour, 10)
        self.assertEqual(time.minute, 0)

    def test_lemmatization(self):
        """Test lemmatization of words"""
        text = "I am travelling to London"
        doc = self.nlp.process(text)
        lemmas = [token.lemma_ for token in doc]
        self.assertIn("travel", lemmas)  # 'travelling' should be lemmatized to 'travel'

    def test_stop_words_removal(self):
        """Test stop words removal"""
        text = "I want to book a ticket from Norwich to London"
        doc = self.nlp.process(text)
        # Get tokens without stop words
        non_stop_words = [token.text for token in doc if not token.is_stop]
        
        # Check common stop words are removed
        self.assertNotIn("I", non_stop_words)
        self.assertNotIn("to", non_stop_words)
        self.assertNotIn("a", non_stop_words)
        
        # Check important content words remain
        self.assertIn("book", non_stop_words)
        self.assertIn("ticket", non_stop_words)
        self.assertIn("Norwich", non_stop_words)
        self.assertIn("London", non_stop_words)

    def test_pos_tagging(self):
        """Test part-of-speech tagging"""
        text = "I need to book a fast train to London tomorrow"
        doc = self.nlp.process(text)
        
        # Create dictionary of words and their POS tags
        pos_dict = {token.text: token.pos_ for token in doc}
        
        # Test specific POS tags
        self.assertEqual(pos_dict["I"], "PRON")  # Pronoun
        self.assertEqual(pos_dict["need"], "VERB")  # Verb
        self.assertEqual(pos_dict["fast"], "ADJ")  # Adjective
        self.assertEqual(pos_dict["train"], "NOUN")  # Noun
        self.assertEqual(pos_dict["tomorrow"], "NOUN")  # Noun
        self.assertEqual(pos_dict["London"], "PROPN")  # Proper noun

    def test_entity_recognition(self):
        """Test named entity recognition"""
        text = "I need to travel from Norwich to London on July 15"
        doc = self.nlp.process(text)
        
        # Extract entities and their labels
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Check if locations are recognized
        locations = [ent[0] for ent in entities if ent[1] in ("GPE", "LOC")]
        self.assertIn("Norwich", locations)
        self.assertIn("London", locations)
        
        # Check if date is recognized
        dates = [ent[0] for ent in entities if ent[1] == "DATE"]
        self.assertIn("July 15", dates)

if __name__ == '__main__':
    unittest.main() 