"""
NLP
"""

from typing import Dict, List, Tuple, Optional
from uuid import UUID

from .task1 import Task1
from .task3 import Task3
from .matcher import  SpacyMatcher
from engine import engine_response, ExpertaResponse

from api.managers import websocket_manager


class NLP:
    """A class for processing natural language text using spaCy.

    This class provides natural language processing capabilities using spaCy's English
    language model. It handles model loading and provides methods for text analysis.
    """

    def __init__(self, conversation_id: UUID):
        """Initialize the NLP processor with spaCy's English language model."""

        self.__task1 = Task1()
        self.__task3 = Task3()

        self.__experta = ExpertaResponse()
        self.__matcher = SpacyMatcher()
        self.conversation_id = conversation_id
        self.__current_task = None


    async def find_best_match(self, user_input: str) -> str:
        """Find the best matching intent for the user input.

        Args:
            user_input (str): User's input text

        Returns:
            Tuple[Optional[str], float]: Best matching intent and its confidence score
        """
        # First check basic intentions using pattern matching

        self.__matcher.set_user_doc(user_input)

        matches = self.__matcher.perform_matching(user_input)

        for match_id, start, end in matches:
            string_id = self.__matcher.get_spacy().vocab.strings[match_id]
            span = self.__matcher.get_user_doc()[start:end]
            print("Match", match_id, span.text, string_id)

            if (
                string_id == "find"
                or string_id == "thank"
                or string_id == "bye"
                or string_id == "greet"
                or string_id == "delay"
                or string_id == "travel"
                or string_id == "incident"
                or string_id == "cancel"
            ):
                engine_response(string_id)

            if string_id == "find":
                self.__current_task = 1

            if string_id == "cancel":
                if self.__current_task == 1:
                    self.__task1.remove_all_info()
                elif self.__current_task == 2:
                    pass
                else:
                    self.__task3.remove_all_info()

                self.__current_task = None
                # engine_response(string_id)


            if string_id == "date":
                self.__task1.set_date_of_travel(span.text)

            if string_id == "time":
                time = ""
                for token in self.__matcher.get_user_doc():
                    if token.ent_type_ == "TIME":
                        print(token.text)
                        time += token.text + " "

                self.__task1.set_time_of_travel(time)

            if string_id == "source":
                source_name = ""
                for token in self.__matcher.get_user_doc():
                    if token.lemma_ == "to":
                        break
                    if token.ent_type_ == "GPE" or token.tag_ in ["NNP", "NNPS", "NNS"]:

                        source_name += token.text.capitalize() + " "
                        # break

                self.__task1.set_source_station(source_name)
                # engine_response("source")

            if string_id == "destination":
                destination_name = ""
                for token in self.__matcher.get_user_doc():
                    if token.lemma_ == "to":
                        destination_name = ""
                    if token.ent_type_ == "GPE" or token.tag_ in ["NNP", "NNPS", "NNS"]:

                        destination_name += token.text.capitalize() + " "

                self.__task1.set_destination_station(destination_name)
                # engine_response("destination")

            if string_id == "location":
                location = []
                for token in self.__matcher.get_user_doc():
                    print(token.text, token.tag_)
                    if token.tag_ == "NNP" or token.ent_type_ == "GPE":
                        location.append(token.text)

                    if token.tag_ == "TIME":
                        self.__task3.set_time_of_incident(token.text)

                self.__task3.set_location_one(location[0])
                self.__task3.set_location_two(location[1])


                # engine_response("location")

            if string_id == "blockage":
                self.__current_task = 3
                self.__task3.set_type_of_contingency("blockage")
                self.__task3.set_type_of_blockage(span.text)

                engine_response("blockage")


            if string_id == "weather":
                self.__current_task = 3
                print(span.text)
                self.__task3.set_type_of_contingency("weather")
                if span.text[-1:] == "s":
                    engine_response("weather_contingency-" + span.text[0:-1])
                else:
                    engine_response("weather_contingency-" + span.text)

                # return self.__experta.get_engine_response()


        if len(matches) == 0:
            print('Hope this not running....')
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

        next_response = None
        print('current task- ', self.__current_task)

        if self.__current_task is not None:
            if self.__current_task == 1:
                task1_response = self.__task1.check_what_info_missing()
                print('task1_response', task1_response)
                if task1_response is None:

                    if self.__task1.check_all_details_gathered():

                        await websocket_manager.send_message(self.conversation_id, "Please wait while we look for a ticket.")

                        cheapest_ticket = self.__task1.run_scraper()
                        print("cheapest_icket", cheapest_ticket)
                        if type(cheapest_ticket) is str:
                            engine_response(cheapest_ticket)
                            return self.__experta.get_engine_response()
                        else:
                            return cheapest_ticket["url"]

                else:
                    next_response = task1_response

            if self.__current_task == 2:
                pass

            if self.__current_task == 3:

                if self.__task3.get_type_of_contingency() == "blockage":
                    if self.__task3.check_all_details_gathered():
                        engine_response(
                            "line_contingency-"
                            + self.__task3.get_location_one()
                            + "-"
                            + self.__task3.get_location_two()
                            + "-"
                            + self.__task3.get_type_of_blockage()
                        )
                        self.__task3.remove_all_info()
                    else:
                        task3_response = self.__task3.check_what_info_missing()
                        if task3_response is not None:
                            next_response = task3_response

                if self.__task3.get_type_of_contingency() == "weather":
                    self.__task3.remove_all_info()

                    pass

                # else:
                #     next_response = task3_response

        if next_response is not None:
            engine_response(next_response)

        return self.__experta.get_engine_response()


    def check_task1_missing_info(self):

        task_1_collected = self.__task1.check_what_info_missing()
        if task_1_collected is None:
            engine_response("got_all")
        else:
            engine_response(task_1_collected)
