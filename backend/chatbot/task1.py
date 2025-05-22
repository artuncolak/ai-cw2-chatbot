
from scraper import MyTrainScrapper, NationalRailScraper
from station import StationService
from datetime import datetime


class Task1:

    def __init__(self):
        self.destination_station = None
        self.source_station = None
        self.time_of_travel = None
        self.date_of_travel = None
        self.confirmed = False
        self.__mytrain_scraper = MyTrainScrapper()
        self.__national_scraper = NationalRailScraper()
        self.__station_service = StationService()



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
        ticket = []
        if len(source_station) == 0 or len(dest_station) == 0:
            self.remove_all_info()
            return "sorry_no_station"

        else:
            m_ticket = self.__mytrain_scraper.run_scrapper(
                source_station[0].my_train_code,
                dest_station[0].my_train_code,
                formatted_date_string,
            )
            # n_ticket = self.__national_scraper.run_scrapper(
            #     source_station[0].code,
            #     dest_station[0].code,
            #     formatted_date_string,
            # )
            print(m_ticket)
            if type(m_ticket) is not str:
                ticket.extend(m_ticket)
            # if type(n_ticket) is list:
            #     ticket.extend(n_ticket)

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

