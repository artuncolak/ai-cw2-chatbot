"""
ChatBot
"""

from datetime import datetime
from uuid import UUID

from fastapi import WebSocket

from .nlp import NLP

CONFIDENCE_THRESHOLD = 0.5


class ChatBot:
    """ChatBot Class"""

    def __init__(self, conversation_id: UUID):
        """Initialize the chatbot with required files and NLP processor."""
        self.__nlp = NLP(conversation_id=conversation_id)

    def _get_current_time(self) -> str:
        """Get the current time in a readable format.

        Returns:
            str: Current time string
        """
        return datetime.now().strftime("%I:%M %p")

    def _get_current_date(self) -> str:
        """Get the current date in a readable format.

        Returns:
            str: Current date string
        """
        return datetime.now().strftime("%A, %B %d, %Y")

    async def get_response(self, user_input: str, websocket: WebSocket) -> str:
        """Generate a response based on user input.

        Args:
            user_input (str): User's input text

        Returns:
            str: Chatbot's response
        """
        # intent, confidence = self.__nlp.find_best_match(user_input)

        # # If no intent matches or confidence is too low
        # if not intent or confidence < CONFIDENCE_THRESHOLD:
        #     return "I'm not sure I understand. Could you please rephrase that?"

        # print("intent:", intent)
        # print("confidence:", confidence)
        # print("confidence:", confidence)
        # # Handle time and date intents
        # match intent:
        #     case "time":
        #         return f"The current time is {self._get_current_time()}"
        #     case "date":
        #         return f"Today is {self._get_current_date()}"
        #     case _:
        #         return self.__nlp.process_basic_intentions(intent)

        return await  self.__nlp.find_best_match(user_input, websocket)

    def get_engine_response(self, response: str) -> str:
        return response
