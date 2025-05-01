


class Task1:

    def __init__(self):
        self.destination_station = None
        self.source_station = None
        self.time_of_travel = None
        self.date_of_travel = None



    def get_destination_station(self):
        return self.destination_station
    def get_source_station(self):
        return self.source_station
    def get_time_of_travel(self):
        return self.time_of_travel
    def get_date_of_travel(self):
        return self.date_of_travel

    def set_destination_station(self, destination_station):
        self.destination_station = destination_station
    def set_source_station(self, source_station):
        self.source_station = source_station
    def set_time_of_travel(self, time_of_travel):
        self.time_of_travel = time_of_travel
    def set_date_of_travel(self, date_of_travel):
        self.date_of_travel = date_of_travel

    def check_all_details_gathered(self):
        if self.destination_station == '' or self.source_station == '' or self.time_of_travel == '' or self.date_of_travel == '':
            return False
        else:
            return True

    def check_what_info_missing(self):
        if self.source_station is None:
            return "source"
        if self.destination_station is None:
            return "destination"
        if self.date_of_travel is None:
            return "date"
        if self.time_of_travel is None:
            return "time"

        return None

        # perform the scrapping

