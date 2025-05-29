from twisted.internet.defer import ensureDeferred
from scraper import MyTrainScraper, NationalRailScraper, NorthernRailwayScraper
from station import StationService
from datetime import datetime

# from backend.scraper import NorthernRailwayScraper


class Task1:

    def __init__(self):
        self.destination_station = None
        self.source_station = None
        self.time_of_travel = None
        self.date_of_travel = None
        self.confirmed = False
        self.__mytrain_scraper = MyTrainScraper()
        self.__national_scraper = NationalRailScraper()
        self.__station_service = StationService()
        self.__northern_rail_scraper = NorthernRailwayScraper()



    def get_destination_station(self):
        return self.destination_station
    def get_source_station(self):
        return self.source_station
    def get_time_of_travel(self):
        return self.time_of_travel
    def get_date_of_travel(self):
        return self.date_of_travel
    def get_confirmed(self):
        return self.confirmed

    def set_destination_station(self, destination_station):
        self.destination_station = destination_station
    def set_source_station(self, source_station):
        self.source_station = source_station
    def set_time_of_travel(self, time_of_travel):
        self.time_of_travel = time_of_travel
    def set_date_of_travel(self, date_of_travel):
        self.date_of_travel = date_of_travel
    def set_confirmed(self, status):
        self.confirmed = status

    def check_all_details_gathered(self):
        if self.destination_station is None or self.source_station is None or self.time_of_travel is None or self.date_of_travel is None or self.confirmed is False:
            return False
        else:
            return True

    def check_what_info_missing(self):
        if self.source_station is None:
            return "source"
        if self.destination_station is None:
            return "destination"
        if self.date_of_travel is None:
            return "travel_date"
        if self.time_of_travel is None:
            return "travel_time"


        return None

    def remove_all_info(self):
        self.source_station = None
        self.destination_station = None
        self.time_of_travel = None
        self.date_of_travel = None
        self.confirmed = False


    def run_scraper(self):
        source_station = self.__station_service.search_by_name(
            self.get_source_station().strip()
        )
        print(source_station)

        dest_station = self.__station_service.search_by_name(
            self.get_destination_station().strip()
        )
        # print(dest_station)

        date_string = (
                self.get_date_of_travel().capitalize()
                + ", 2025 "
                + self.get_time_of_travel().upper()
        )
        print(date_string)
        date_format = "%B %d, %Y %I:%M %p"
        datetime_object = datetime.strptime(date_string.strip(), date_format)
        # print(datetime_object)
        formatted_date_string = datetime_object.strftime("%Y-%m-%dT%H:%M:%SZ")
        # print(formatted_date_string)

        north_month = datetime_object.strftime("%m")
        north_date= datetime_object.strftime("%d")
        north_min = datetime_object.strftime("%M")
        north_hour = datetime_object.strftime("%H")
        # print(now.strftime("%I:%M %p"))

        # print(formatted_date_string1, formatted_date_string2, formatted_date_string3, formatted_date_string4)
        # print(formatted_date_string.strftime("%B %d"))
        # "29%2F05%2F2025"
        north_date_format = f"{north_date}%2F0{north_month}%2F02025"
        north_time_format = f"{north_hour}%3A{north_min}"

        ticket = []

        # return "sorry_no_station"
        if len(source_station) == 0 or len(dest_station) == 0:
            self.remove_all_info()
            return "sorry_no_station"

        else:

            try:
                n_ticket = self.__national_scraper.run_scrapper(
                     source=source_station[0].code,
                     destination=dest_station[0].code,
                     leaving_date_time=formatted_date_string,
                     leaving_type="DepartingAt",
                     returning_type=None,
                     return_date_time=None,
                     adults=1,
                     children=0,
                     railcards=[['YNG', 1]],
                 )
                async def get_nrscraper():
                     if len(await n_ticket) != 0:
                         ticket.extend(await n_ticket)
                ensureDeferred(get_nrscraper())
#                print(n_ticket)
            except:
                pass

            try:
               m_ticket = self.__mytrain_scraper.run_scrapper(
                   source=source_station[0].my_train_code,
                   destination=dest_station[0].my_train_code,
                   leaving_date_time=formatted_date_string,
                   leaving_type="DepartingAt",
                   returning_type=None,
                   return_date_time=None,
                   adults=1,
                   children=0,
                   railcards=[['YNG', 1]],)
               if len(m_ticket) != 0:
                   ticket.extend(m_ticket)
#               print(m_ticket)
            except:
                pass

            try:
                north_ticket = self.__northern_rail_scraper.run_scraper(
                    source=source_station[0].code,
                    destination=dest_station[0].code,
                    leaving_date=north_date_format,
                    leaving_time=north_time_format,
                    leaving_type="DepartingAt",
                    )
                if len(north_ticket) != 0:
                    ticket.extend(north_ticket)
#                print(north_ticket)
            except:
                pass

        print(ticket)

        if len(ticket) == 0:
            self.remove_all_info()
            return 'sorry_task1'

        mindict = {"price": float('inf')}
        try:
            for item in ticket:
                if "price" not in item:
                    pass
                elif item["price"] < mindict["price"]:
                    mindict = item
        except:
            # raise ConnectionError("Could not connect to website")
            self.remove_all_info()
            return "sorry_task1"


        if mindict == {"price": float('inf')}:
            # raise ConnectionError("Could not connect to website")
            return "sorry_task1"

        else:
            print(f"This is the cheapest item: {mindict}")

        self.remove_all_info()
        print(mindict)
        if len(ticket) == 0 or ticket is None:
            return "sorry_task1"
            # return self.__experta.get_engine_response()
        return mindict

