"""
NLP
"""
import datetime
from typing import Dict, List, Tuple, Optional
from uuid import UUID

from fastapi import WebSocket

from .task1 import Task1
from .task2 import Task2
from .task3 import Task3
from .matcher import  SpacyMatcher
from engine import engine_response, ExpertaResponse
from prediction.prediction_service import PredictionService

from api.managers import websocket_manager


class NLP:
    """A class for processing natural language text using spaCy.

    This class provides natural language processing capabilities using spaCy's English
    language model. It handles model loading and provides methods for text analysis.
    """

    def __init__(self, conversation_id: UUID):
        """Initialize the NLP processor with spaCy's English language model."""

        self.__task1 = Task1()
        self.__task2 = Task2()
        self.__task3 = Task3()
        self.__experta = ExpertaResponse()
        self.__matcher = SpacyMatcher()
        self.conversation_id = conversation_id
        self.__current_task = None


    async def find_best_match(self, user_input: str, websocket: WebSocket) -> str:
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

            if string_id == "delay":
                self.__current_task = 2

            if string_id == "confirm" and self.__current_task == 1:
                self.__task1.set_confirmed(True)

            if string_id == "confirm" and self.__current_task == 2:
                self.__task2.set_confirmed(True)

            if string_id == "confirm" and self.__current_task == 3:
                self.__task3.set_confirmed(True)


            if string_id == "cancel":
                if self.__current_task == 1:
                    self.__task1.remove_all_info()
                elif self.__current_task == 2:
                    self.__task2.remove_all_info()
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
                        time += token.text + " "

                    print('CURRENT TASK', self.__current_task)
                    print(token.text, token.ent_type_, token.tag_, token.lemma_)

                    if self.__current_task == 2 and token.tag_ == "CD":
                            self.__task2.set_delay(token.text)

                if self.__current_task == 1:
                    self.__task1.set_time_of_travel(time)

            if string_id == "source" or string_id == "current":
                source_name = ""
                for token in self.__matcher.get_user_doc():
                    if token.lemma_ == "to":
                        break
                    if token.ent_type_ == "GPE" or token.tag_ in ["NNP", "NNPS", "NNS"]:

                        source_name += token.text.capitalize() + " "
                        # break

                if self.__current_task == 1:
                    self.__task1.set_source_station(source_name)
                else:
                    self.__task2.set_current_station(source_name)
                # engine_response("source")

            if string_id == "destination":
                destination_name = ""
                for token in self.__matcher.get_user_doc():
                    print(token.text, token.lemma_, token.ent_type_, token.tag_)
                    if token.lemma_ == "to":
                        destination_name = ""
                    if token.ent_type_ == "GPE" or token.tag_ in ["NNP", "NNPS", ] and token.ent_type_ is not "DATE":

                        destination_name += token.text.capitalize() + " "

                if self.__current_task == 1:
                    self.__task1.set_destination_station(destination_name)
                else:
                    self.__task2.set_destination_station(destination_name)
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

            if string_id == "today":
                if self.__current_task == 1:

                    now = datetime.datetime.now()
                    # print(now.strftime("%B %d"))

                    self.__task1.set_date_of_travel(now.strftime("%B %d"))
                    # print(now.strftime("%I:%M %p"))

            if string_id == "tomorrow":
                if self.__current_task == 1:
                    today = datetime.date.today()
                    tomorrow = today + datetime.timedelta(days=1)
                    # print(tomorrow.strftime("%B %d"))
                    self.__task1.set_date_of_travel(tomorrow.strftime("%B %d"))
                    # print(tomorrow.strftime("%I:%M %p"))


            # if string_id == "minute":
            #     print(span.text)
            #     for token in self.__matcher.get_user_doc():
            #         print(token.text, token.tag_)
            #         if token.ent_type_ == "CD":
            #             self.__task2.set_delay(token.text)



        if len(matches) == 0:
            print('Hope this not running....')
            engine_response("")

        print("TASK 1 INFO ")
        print(self.__task1.get_time_of_travel())
        print(self.__task1.get_date_of_travel())
        print(self.__task1.get_source_station())
        print(self.__task1.get_destination_station())

        print("TASK 2 INFO ")
        print(self.__task2.get_current_station())
        print(self.__task2.get_destination_station())
        print(self.__task2.get_delay())
        # print(self.__task1.get_destination_station())

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

                    if self.__task1.get_confirmed() is False:
                        confirmation_message = "<b>Your search:</b> <br> Source: " + self.__task1.get_source_station() + "<br> Destination: " + self.__task1.get_destination_station() + "<br> Date: " + self.__task1.get_date_of_travel() + "<br> Time: " + self.__task1.get_time_of_travel() + "<br> Please type 'yes' to confirm, 'no' to reset."

                        return confirmation_message

                    if self.__task1.check_all_details_gathered():

                        await websocket_manager.send_message(self.conversation_id, "Please wait while we look for a ticket.")

                        cheapest_ticket = self.__task1.run_scraper()
                        print("cheapest_icket", cheapest_ticket)
                        if type(cheapest_ticket) is str:
                            engine_response(cheapest_ticket)
                            return self.__experta.get_engine_response()
                        else:
                            self.__current_task = None
                            return cheapest_ticket["url"]

                else:
                    next_response = task1_response

            if self.__current_task == 2:

                task2_response = self.__task2.check_what_info_missing()

                print('task2_response', task2_response)
                if task2_response is None:

                    if self.__task2.get_confirmed() is False:
                        confirmation_message = "<b>Your search:</b> <br> Current Station: " + self.__task2.get_current_station() + "<br> Destination Station: " + self.__task2.get_destination_station() + "<br> Current Delay(mins): " + self.__task2.get_delay() + "<br> Please type 'yes' to confirm, 'no' to reset."
                        return confirmation_message

                    if self.__task2.check_all_details_gathered():

                        await websocket_manager.send_message(self.conversation_id,
                                                             "Please wait while we calculate the delay.")

                        prediction_service: PredictionService = websocket.app.state.prediction_service
                        current_station = self.__task2.search_current_station()
                        destination_station = self.__task2.search_destination_station()



                        if len(current_station) == 0 or len(destination_station) == 0:
                            next_response = "sorry_no_station"
                            self.__task2.remove_all_info()
                        else:
                            print(current_station[0].code)
                            print(destination_station[0].code)
                            try:
                                # print('PRdiction')
                                prediction = prediction_service.predict_arrival_time(
                                current_station=current_station[0].code, destination_station=destination_station[0].code, current_delay=int(self.__task2.get_delay().strip())
                                )
                                print(prediction)
                                self.__task2.remove_all_info()
                                return "<b>Delay at " + prediction['destination'] + ": </b> <span class='text-rose-700 font-semibold'>" + str(prediction['propagated_delay']) + " min. </span>" + "<br> Current Time: " + prediction['current_time'] + "<br> <b>ETA:</b> " + prediction['predicted_arrival_time'] + "<br> Estimated Journey time: " + str(prediction['estimated_journey_time']) + " min."
                            except:
                                self.__task2.remove_all_info()
                                return "Something went wrong. Please try again."

                        # print(prediction)
                        # return prediction

                else:
                    next_response = task2_response


            if self.__current_task == 3:

                if self.__task3.get_type_of_contingency() == "blockage":
                    if self.__task3.check_all_details_gathered():

                        if self.__task3.get_confirmed() is False:
                            confirmation_message = "<b>Incident details:</b> <br> Type: Line " + self.__task3.get_type_of_contingency() + "<br> Location: " + self.__task3.get_location_one() + "-" + self.__task3.get_location_two() + "<br> Blockage: " + self.__task3.get_type_of_blockage().upper() + "<br> Please type 'yes' to confirm, 'no' to reset."

                            return confirmation_message

                        engine_response(
                            "line_contingency-"
                            + self.__task3.get_location_one()
                            + "-"
                            + self.__task3.get_location_two()
                            + "-"
                            + self.__task3.get_type_of_blockage()
                        )

                        self.__task3.remove_all_info()
                        self.__current_task = None
                    else:
                        task3_response = self.__task3.check_what_info_missing()
                        if task3_response is not None:
                            next_response = task3_response

                if self.__task3.get_type_of_contingency() == "weather":
                    self.__task3.remove_all_info()
                    self.__current_task = None
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
