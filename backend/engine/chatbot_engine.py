
from experta import *

import warnings
import json
from typing import Dict

warnings.filterwarnings('ignore')
from .experta_response import ExpertaResponse
SENTENCES_FILE = "engine/sentences.json"


def load_intentions(file_path: str) -> Dict:
    """Load and parse the intentions JSON file.

    Args:
        file_path (str): Path to the intentions JSON file

    Returns:
        Dict: Parsed intentions data
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
"""
Expert system 
    The aim of the expert system is to take knowledge from a human expert and convert this into a number of
    hardcoded rules to apply to the input data.
    A classic example of a rule based system is the domain-specific expert system that uses rules to make deductions
    or choices.
    For eg: an expert system might help a doctor choose diagnosis based on a cluster of symptoms.

Basic:
    An expert system is a program capable of pairing up a set of facts with a set of rules to those facts, and 
    execute some actions based on the matching rules.

Facts:
    Facts are the basic unit of information of Experta. They are used by the system to reason about the problem.

Rules:
    In their most basic form, the rules are commonly conditional statements (if a, then do x, else if b, then do y)

Experta:
    Python lib for building expert systems strongly inspired by CLIPS

    The goal is to recognize the type of train ticket(according to user's input) with the Expert System
        and give a suitable answer to the user according to it.

    You might say that this operation could also be implemented with a simple if-else condition.True,but it should
    be kept in mind that this is just for introduction and for a bigger project (CW002) you will understand the 
    importance of Expert system.

"""

final_chatbot = False
response = ExpertaResponse()
answer = ''
sentences = load_intentions(SENTENCES_FILE)
# print(sentences)

class Greeting(Fact):  # define fact
    ''' Info about the booking ticket'''


    pass

class Book(Fact):
    pass

class Task3(Fact):
    pass

class Contingency(Fact):
    station_one = Field(str, mandatory=True)
    station_two = Field(str, mandatory=True)
    type = Field(str, mandatory=True)

class TrainBot(KnowledgeEngine):

    @DefFacts()
    def default_response(self):
        set_response('I am not sure how to respond to this question.')
        yield Fact(Greeting="I am not sure how to respond")

        # for fact in sentences:
        #     print(fact)
        #     yield Fact(Contingency=fact)

    @Rule(Greeting(input='greet'))
    def greet_back(self):
        # print("BOT: you have selected a one way ticket. Have a good trip.")
        # if final_chatbot:
        #     print("BOT: If you don't have any other question, you can type bye.")
        response.set_engine_response('Hi, thanks for checking in. How can I help you?')
        # find_response("colchester-manningtree-partial")
        # return 'Hi, thanks for checking in.'


    @Rule(Greeting(input='bye'))
    def say_bye(self):
        response.set_engine_response('Thank you for using this service,Goodbye.')
        # if final_chatbot:
        #     print("BOT: If you don't have any other question, you can type bye.")

    @Rule(Greeting(input='thank'))
    def say_thanks(self):
        # print("BOT: you have selected a " + ticket["ticket"] + ". Have a good trip.")
        set_response('Happy to help. Anything else?')
        # if final_chatbot:
        #     print("BOT: If you don't have any other question, you can type bye.")
        # response.set_engine_response('Happy to help.')

    @Rule(OR(Book(input='train'),Book(input='ticket'),Book(input='book')))
    def ask_source_station(self):
        set_response('Sure. What is your source station?')

    @Rule(Book(input='find'))
    def reply_find(self):
        set_response('Sure. What is your source station?')

    @Rule(OR(Book(input='source'), Book(input='board'), Book(input='start'), Book(input='begin')))
    def ask_destination_station(self):
        set_response('Understood. What is your destination station?')

    @Rule(OR(Book(input='destination'), Book(input='last'), Book(input='final'), Book(input='end'), Book(input='deboard')))
    def ask_date_of_travel(self):
        set_response('Noted. When you are planning to travel?')

    @Rule(AS.user_input << Book(input=L('open') | L('return') | L('single')))
    def ticket_type(self, user_input):
        # print("BOT: you have selected a " + user_input["input"] + ".")
        set_response("BOT: you have selected a " + user_input["input"] + ".")
        # if final_chatbot:
        #     print("BOT: If you don't have any other question, you can type bye.")

    @Rule(Book(input='date'))
    def say_date(self):
        # print("BOT: you have selected a date of travel.")
        set_response('Alright. What is your date of travel?')

    @Rule(Book(input='time'))
    def say_time(self):
        # print("BOT: you have selected a date of travel.")
        set_response('Alright. What is your time of travel?')

    @Rule(Book(input='delay'))
    def say_delay(self):
        # print("BOT: you have selected a date of travel.")
        set_response('I can help you with that. Which train are you on?')

    @Rule(Book(input='travel'))
    def reply_travel(self):
        # print("BOT: you have selected a date of travel.")
        set_response('I am thinking about this.')

    @Rule(Book(input='got_all'))
    def say_got_all(self):
        set_response("I got all info, Please wait while I find the cheapest ticket for you.")

    @Rule(Book(input='sorry'))
    def say_sorry(self):
        set_response("Sorry, I have missed some of the important info.")


    @Rule(Task3(input='incident'))
    def say_incident(self):
        set_response("Sure. What is the location of the incident?")

    @Rule(Task3(input='location'))
    def say_location(self):
        set_response("Noted. Has it caused partial or full line blockage")

    @Rule(Task3(input='blockage'))
    def say_blockage(self):
        set_response("Understood. What would be the approximate time of incident?")

    @Rule(Task3(input='blockage_time'))
    def say_blockage(self):
        set_response("Understood. Please wait while I generate a response.")

    # @Rule(Contingency("colchester","manningtree",Contingency(input="partial")))
    # def say_partial_1(self):
    #     set_response("colchester-manningtree-partial")
    #     find_response("colchester-manningtree-partial")

    @Rule(Contingency(station_one='colchester', station_two='manningtree', type='partial'))
    def say_partial_cm(self):
        set_response(find_response("colchester-manningtree-partial"))
        # find_response("colchester-manningtree-partial")

    @Rule(Contingency(station_one='colchester', station_two='manningtree', type='full'))
    def say_full_cm(self):
        set_response(find_response("colchester-manningtree-full"))


def engine_response(user_input):
    engine = TrainBot()
    engine.reset()
    # word =
    # up = ''
    if 'contingency' in user_input:
        up = user_input.split('-')
        engine.declare(Contingency(station_one=up[1], station_two=up[2], type=up[3]))
        engine.run()
    else:
        if user_input is not None:

            engine.declare(Greeting(input=user_input),Book(input=user_input), Task3(input=user_input))
            # engine.declare(Book(user_input))   # adds a new fact to the list of factlist
            # engine.declare(Contingency(station_one=up[1], station_two=up[2], type=up[3]))
            engine.run()

        return True

    return False


def set_response(current_response):
    response.set_engine_response(current_response)


def find_response(user_input):
    # user_input_lower = user_input.lower()
    # for intent, data in sentences.items():
    #     if any(pattern in user_input_lower for pattern in data["patterns"]):
    #         return intent, 1.0
    triggers = user_input.split('-')
    print(sentences[triggers[0]+'-'+triggers[1]][triggers[2]])
    plan = sentences[triggers[0]+'-'+triggers[1]][triggers[2]]
    response = ''
    for key, value in plan.items():
        response += '<b>'+key+'</b>' + ' : ' + value + '<br>'


    return response
    # for word in user_input.split(' '):
    #     for type_of_intention in sentences[user_input]:
    #         if word.lower() in sentences[type_of_intention]["patterns"]:
    #             # print(sentences[type_of_intention]['responses'])
    #             # for key, values in sentences[type_of_intention]:
    #             responses = sentences[type_of_intention]["responses"]
    #             print(type(responses))
    #             for key, value in responses.items():
    #                 print("LOOOOOKKKKK ", key, value)
    #                 # if values == "responses":
                    #
                    #     for value in values:
                    #         print(value)

                # Do not change these lines
                # if type_of_intention == 'greeting' and final_chatbot:
                #     print("BOT: We can talk about the time, date, and train tickets.\n(Hint: What time is it?)")
                # return type_of_intention
    # return None