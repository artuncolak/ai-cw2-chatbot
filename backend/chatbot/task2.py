
from station import StationService


class Task2:

    def __init__(self):
        self.current_station = None
        self.destination_station = None
        self.delay = None
        self.confirmed = False
        self.__station_service = StationService()




    def get_current_station(self):
        return self.current_station
    def get_destination_station(self):
        return self.destination_station
    def get_delay(self):
        return self.delay
    # def get_type_of_blockage(self):
    #     return self.type_of_blockage
    # def get_type_of_contingency(self):
    #     return self.type_of_contingency
    def get_confirmed(self):
        return self.confirmed

    def set_current_station(self, source_station):
        self.current_station = source_station
    def set_destination_station(self, destination_station):
        self.destination_station = destination_station
    def set_delay(self, delay):
        self.delay = delay
    def set_confirmed(self, status):
        self.confirmed = status

    def check_all_details_gathered(self):

        if self.destination_station is None or self.current_station is None or self.delay is None or self.confirmed is False:
            return False
        return True

    def check_what_info_missing(self):
        if self.current_station is None:
            return "current_station"
        if self.destination_station is None:
            return "destination_station"
        if self.delay is None:
            return "delay_time"

        return None

    def remove_all_info(self):
        self.current_station = None
        self.destination_station = None
        self.confirmed = False
        self.delay = None

    def search_current_station(self):
        print("search_current_station1", self.get_current_station().strip())
        print("search_current_station", self.__station_service.search_by_name(self.get_current_station().strip))
        return self.__station_service.search_by_name(
            self.get_current_station().strip()
        )

    def search_destination_station(self):
        return self.__station_service.search_by_name(
            self.get_destination_station().strip()
        )


