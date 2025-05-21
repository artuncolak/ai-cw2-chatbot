import unittest
from experta import Fact
from engine.chatbot_engine import TrainBot, Greeting, Book, Task3, WeatherContingency, LineContingency
from engine.experta_response import ExpertaResponse


class TestChatbotEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TrainBot()
        self.response = ExpertaResponse()

    def test_greeting_rule(self):
        """Test basic greeting rule"""
        self.engine.reset()  # Reset the engine's working memory
        self.engine.declare(Greeting(input="greet"))
        self.engine.run()
        result = self.response.get_engine_response()
        self.assertIn("hi", result.lower())
        self.assertIn("help", result.lower())

    def test_farewell_rules(self):
        """Test farewell and thank you rules"""
        # Test goodbye
        self.engine.reset()
        self.engine.declare(Greeting(input="bye"))
        self.engine.run()
        result = self.response.get_engine_response()
        self.assertIn("goodbye", result.lower())
        
        # Test thank you
        self.engine.reset()
        self.engine.declare(Greeting(input="thank"))
        self.engine.run()
        result = self.response.get_engine_response()
        self.assertIn("happy to help", result.lower())

    def test_booking_rule(self):
        """Test ticket booking rule"""
        self.engine.reset()
        self.engine.declare(Book(input="ticket"))
        self.engine.run()
        result = self.response.get_engine_response()
        self.assertIn("source", result.lower())

    def test_additional_booking_rules(self):
        """Test various booking-related rules"""
        test_cases = [
            ("find", "source station"),
            ("cancel", "what's next"),
            ("destination", "destination"),
            ("source", "source station"),
            ("travel_date", "date of travel"),
            ("travel_time", "time of travel"),
            ("travel", "thinking about this"),
            ("got_all", "cheapest ticket"),
        ]
        
        for input_text, expected_response in test_cases:
            self.engine.reset()
            self.engine.declare(Book(input=input_text))
            self.engine.run()
            result = self.response.get_engine_response()
            self.assertIn(expected_response.lower(), result.lower())

    def test_ticket_type_rules(self):
        """Test ticket type selection rules"""
        ticket_types = ["open", "return", "single"]
        for ticket_type in ticket_types:
            self.engine.reset()
            self.engine.declare(Book(input=ticket_type))
            self.engine.run()
            result = self.response.get_engine_response()
            self.assertIn(ticket_type, result.lower())
            self.assertIn("selected", result.lower())

    def test_delay_rule(self):
        """Test delay prediction rule"""
        self.engine.reset()
        self.engine.declare(Book(input="delay"))
        self.engine.run()
        result = self.response.get_engine_response()
        self.assertIn("which train", result.lower())

    def test_error_handling_rules(self):
        """Test error handling responses"""
        error_cases = {
            "sorry": "missed some",
            "sorry_task1": "try later",
            "sorry_no_station": "check the names"
        }
        
        for error, expected_text in error_cases.items():
            self.engine.reset()
            self.engine.declare(Book(input=error))
            self.engine.run()
            result = self.response.get_engine_response()
            self.assertIn("sorry", result.lower())
            self.assertIn(expected_text.lower(), result.lower())

    def test_contingency_rule(self):
        """Test contingency plan rule"""
        self.engine.reset()
        self.engine.declare(Task3(input="incident"))
        self.engine.run()
        result = self.response.get_engine_response()
        self.assertIn("location", result.lower())

    def test_weather_contingency_rules(self):
        """Test weather contingency responses"""
        weather_conditions = ["frost", "snow", "flood", "temp", "wind", "autumn"]
        for condition in weather_conditions:
            self.engine.reset()
            self.engine.declare(WeatherContingency(input=condition))
            self.engine.run()
            result = self.response.get_engine_response()
            self.assertIsNotNone(result)
            self.assertNotEqual(result, "")

    def test_line_contingency_rules(self):
        """Test line contingency responses for different station pairs"""
        test_cases = [
            ("colchester", "manningtree", "partial"),
            ("colchester", "manningtree", "full"),
            ("manningtree", "ipswich", "partial"),
            ("manningtree", "ipswich", "full"),
            ("ipswich", "stowmarket", "partial"),
            ("ipswich", "stowmarket", "full"),
            ("stowmarket", "diss", "partial"),
            ("stowmarket", "diss", "full"),
            ("diss", "norwich", "partial"),
            ("diss", "norwich", "full")
        ]
        
        for station1, station2, blockage_type in test_cases:
            self.engine.reset()
            self.engine.declare(LineContingency(
                station_one=station1,
                station_two=station2,
                type=blockage_type
            ))
            self.engine.run()
            result = self.response.get_engine_response()
            self.assertIsNotNone(result)
            self.assertNotEqual(result, "")

    def test_default_rule(self):
        """Test default rule for unknown inputs"""
        self.engine.reset()
        facts = self.engine.run()  # This will trigger the default facts
        # The default response is yielded as a Fact with a Greeting field
        default_response = next(
            fact
            for fact in self.engine.facts.values()
            if isinstance(fact, Fact) and "Greeting" in fact
        )
        self.assertIn("not sure", default_response["Greeting"].lower())


if __name__ == "__main__":
    unittest.main()
