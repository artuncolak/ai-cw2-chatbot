


class Task3:

    def __init__(self):
        self.location_one = None
        self.location_two = None
        self.time_of_incident = None
        self.type_of_blockage = None



    def get_location_one(self):
        return self.location_one
    def get_location_two(self):
        return self.location_two
    def get_time_of_incident(self):
        return self.time_of_incident
    def get_type_of_blockage(self):
        return self.type_of_blockage

    def set_location_one(self, location_one):
        self.location_one = location_one
    def set_location_two(self, location_two):
        self.location_two = location_two
    def set_time_of_incident(self, time_of_incident):
        self.time_of_incident = time_of_incident
    def set_type_of_blockage(self, type_of_blockage):
        self.type_of_blockage = type_of_blockage

    def check_all_details_gathered(self):
        if self.location_one is None or self.location_two is None or self.time_of_incident is None or self.type_of_blockage is None:
            return False
        else:
            return True

    def check_what_info_missing(self):
        if self.location_one is None:
            return "location_one"
        if self.location_two is None:
            return "location_two"
        if self.type_of_blockage is None:
            return "blockage_type"
        if self.time_of_incident is None:
            return "blockage_time"

        return None

