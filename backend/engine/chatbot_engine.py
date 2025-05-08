
from experta import *

import warnings
import json
from typing import Dict

warnings.filterwarnings('ignore')
from .experta_response import ExpertaResponse
CONTINGENCY_FILE = "engine/contingencies.json"
WEATHER_FILE = "engine/weather_contingency.json"


def load_contingencies(file_path: str) -> Dict:
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
line_block_contingencies = load_contingencies(CONTINGENCY_FILE)
weather_contingencies = load_contingencies(WEATHER_FILE)

class Greeting(Fact):  # define fact
    ''' Info about the booking ticket'''
    pass

class Book(Fact):
    pass

class Task3(Fact):
    pass

class LineContingency(Fact):
    station_one = Field(str, mandatory=True)
    station_two = Field(str, mandatory=True)
    type = Field(str, mandatory=True)

class WeatherContingency(Fact):
    pass

class TrainBot(KnowledgeEngine):

    @DefFacts()
    def default_response(self):
        set_response('I am not sure how to respond to this question.')
        yield Fact(Greeting="I am not sure how to respond")

        # for fact in contingencies:
        #     print(fact)
        #     yield Fact(LineContingency=fact)

    @Rule(Greeting(input='greet'))
    def greet_back(self):
        response.set_engine_response('Hi, thanks for checking in. How can I help you?')

    @Rule(Greeting(input='bye'))
    def say_bye(self):
        response.set_engine_response('Thank you for using this service,Goodbye.')

    @Rule(Greeting(input='thank'))
    def say_thanks(self):

        set_response('Happy to help. Anything else?')


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
        set_response("BOT: you have selected a " + user_input["input"] + ".")

    @Rule(Book(input='date'))
    def say_date(self):
        set_response('Alright. What is your date of travel?')

    @Rule(Book(input='time'))
    def say_time(self):
        set_response('Alright. What is your time of travel?')

    @Rule(Book(input='delay'))
    def say_delay(self):
        set_response('I can help you with that. Which train are you on?')

    @Rule(Book(input='travel'))
    def reply_travel(self):
        set_response('I am thinking about this.')

    @Rule(Book(input='got_all'))
    def say_got_all(self):
        set_response("I got all info, Please wait while I find the cheapest ticket for you.")

    @Rule(Book(input='sorry'))
    def say_sorry(self):
        set_response("Sorry, I have missed some of the important info.")

    @Rule(Book(input='sorry_task1'))
    def say_sorry_task1(self):
        set_response("Sorry, Something went wrong. Please try again.")

    @Rule(Book(input='sorry_no_station'))
    def say_sorry_no_station(self):
        set_response("Sorry, I could not find the relevant station. Please check the names and try again.")

    @Rule(Task3(input='incident'))
    def say_incident(self):
        set_response("Sure. What is the location of the incident?")

    @Rule(Task3(input='location'))
    def say_location(self):
        set_response("Noted. Has it caused partial or full line blockage")

    @Rule(AS.user_input << WeatherContingency(input=L('frost') | L('snow') | L('flood') | L('temp') | L('wind') | L('autumn')))
    def say_weather(self, user_input):
        # set_response("Noted. Has it caused partial or full line blockage")
        set_response(weather_response(user_input["input"]))


    @Rule(Task3(input='blockage'))
    def say_blockage(self):
        set_response("Understood. What would be the approximate time of incident?")

    @Rule(Task3(input='blockage_time'))
    def say_blockage(self):
        set_response("Understood. Please wait while I generate a response.")

    # @Rule(LineContingency("colchester","manningtree",LineContingency(input="partial")))
    # def say_partial_1(self):
    #     set_response("colchester-manningtree-partial")
    #     find_response("colchester-manningtree-partial")

    @Rule(LineContingency(station_one='colchester', station_two='manningtree', type='partial'))
    def say_partial_cm(self):
        set_response(line_response("colchester-manningtree-partial"))

    @Rule(LineContingency(station_one='colchester', station_two='manningtree', type='full'))
    def say_full_cm(self):
        set_response(line_response("colchester-manningtree-full"))

    @Rule(LineContingency(station_one='manningtree', station_two='ipswich', type='partial'))
    def say_partial_mi(self):
        set_response(line_response("manningtree-ipswich-partial"))

    @Rule(LineContingency(station_one='manningtree', station_two='ipswich', type='full'))
    def say_full_mi(self):
        set_response(line_response("manningtree-ipswich-partial"))

    @Rule(LineContingency(station_one='manningtree', station_two='ipswich', type='partial'))
    def say_partial_cm(self):
        set_response(line_response("manningtree-ipswich-partial"))

    @Rule(LineContingency(station_one='manningtree', station_two='ipswich', type='full'))
    def say_full_cm(self):
        set_response(line_response("manningtree-ipswich-partial"))

    @Rule(LineContingency(station_one='ipswich', station_two='stowmarket', type='partial'))
    def say_partial_is(self):
        set_response(line_response("ipswich-stowmarket-partial"))

    @Rule(LineContingency(station_one='ipswich', station_two='stowmarket', type='full'))
    def say_full_is(self):
        set_response(line_response("ipswich-stowmarket-full"))

    @Rule(LineContingency(station_one='stowmarket', station_two='diss', type='partial'))
    def say_partial_sd(self):
        set_response(line_response("stowmarket-diss-partial"))

    @Rule(LineContingency(station_one='stowmarket', station_two='diss', type='full'))
    def say_full_sd(self):
        set_response(line_response("stowmarket-diss-full"))

    @Rule(LineContingency(station_one='diss', station_two='norwich', type='partial'))
    def say_partial_dn(self):
        set_response(line_response("diss-norwich-partial"))

    @Rule(LineContingency(station_one='diss', station_two='norwich', type='full'))
    def say_full_dn(self):
        set_response(line_response("diss-norwich-full"))

def engine_response(user_input):
    engine = TrainBot()
    engine.reset()

    if 'line_contingency' in user_input:
        up = user_input.split('-')
        engine.declare(LineContingency(station_one=up[1], station_two=up[2], type=up[3]))
        engine.run()
    elif 'weather_contingency' in user_input:
        wth = user_input.split('-')
        engine.declare(WeatherContingency(input=wth[1]))
        engine.run()
    else:
        if user_input is not None:

            engine.declare(Greeting(input=user_input),Book(input=user_input), Task3(input=user_input))
            # engine.declare(Book(user_input))   # adds a new fact to the list of factlist
            # engine.declare(LineContingency(station_one=up[1], station_two=up[2], type=up[3]))
            engine.run()

        return True

    return False


def set_response(current_response):
    response.set_engine_response(current_response)


def line_response(user_input):

    triggers = user_input.split('-')
    # print(contingencies[triggers[0]+'-'+triggers[1]][triggers[2]])
    plan = line_block_contingencies[triggers[0]+'-'+triggers[1]][triggers[2]]

    if plan is None or plan == '':
        return "There is no contingency plan for this route."

    contingency_response = ''
    for key, value in plan.items():
        if type(value) is list:
            contingency_response += '<b>'+key+':</b><br>'+ setup_html_response(value)
        else:
            contingency_response += '<b>' + key + ':</b><br>' + value + '<br>'

    return contingency_response
  
def weather_response(user_input):
    print('here here',user_input)
    # triggers = user_input.split('-')
    plan = weather_contingencies[user_input]
    print(plan)
    if plan is None or plan == '':
        return "There is no contingency plan for this weather."

    contingency_response = ''
    contingency_response += '<b>' + user_input + ':</b><br>' + setup_html_response(plan)

    return contingency_response

def setup_html_response(text_input):
    html_response = '<ul class="list-disc pl-5">'
    for text in text_input:
        html_response += '<li>' + text + '</li>'
    html_response += '</ul>'
    return html_response

