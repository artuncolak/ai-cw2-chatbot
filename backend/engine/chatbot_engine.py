
from experta import *

import warnings

warnings.filterwarnings('ignore')
from .experta_response import ExpertaResponse

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


class Greeting(Fact):  # define fact
    ''' Info about the booking ticket'''


    pass

class Book(Fact):
    pass

class TrainBot(KnowledgeEngine):

    @DefFacts()
    def default_response(self):
        set_response('I am not sure how to respond to this question.')
        yield Fact(Greeting="I am not sure how to respond")

    @Rule(Greeting(input='greet'))
    def greet_back(self):
        # print("BOT: you have selected a one way ticket. Have a good trip.")
        # if final_chatbot:
        #     print("BOT: If you don't have any other question, you can type bye.")
        response.set_engine_response('Hi, thanks for checking in. How can I help you?')
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
        set_response('Alright. What is your time of travel?')

    @Rule(Book(input='time'))
    def say_time(self):
        # print("BOT: you have selected a date of travel.")
        set_response('Alright. What is your date of travel?')

    @Rule(Book(input='delay'))
    def say_delay(self):
        # print("BOT: you have selected a date of travel.")
        set_response('I can help you with that. Which train are you on?')

    @Rule(Book(input='travel'))
    def reply_travel(self):
        # print("BOT: you have selected a date of travel.")
        set_response('I am thinking about this.')

def engine_response(user_input):
    engine = TrainBot()
    engine.reset()

    if user_input is not None:
        print('Clllled')
        engine.declare(Greeting(input=user_input),Book(input=user_input))
        # engine.declare(Book(user_input))   # adds a new fact to the list of factlist
        engine.run()

        return True

    return False


def set_response(current_response):
    response.set_engine_response(current_response)



