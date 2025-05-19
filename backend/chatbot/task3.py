


class Task3:

    def __init__(self):
        self.location_one = None
        self.location_two = None
        self.time_of_incident = None
        self.type_of_blockage = None
        self.type_of_contingency = None



    def get_location_one(self):
        return self.location_one
    def get_location_two(self):
        return self.location_two
    def get_time_of_incident(self):
        return self.time_of_incident
    def get_type_of_blockage(self):
        return self.type_of_blockage
    def get_type_of_contingency(self):
        return self.type_of_contingency

    def set_location_one(self, location_one):
        self.location_one = location_one
    def set_location_two(self, location_two):
        self.location_two = location_two
    def set_time_of_incident(self, time_of_incident):
        self.time_of_incident = time_of_incident
    def set_type_of_blockage(self, type_of_blockage):
        self.type_of_blockage = type_of_blockage
    def set_type_of_contingency(self, type_of_contingency):
        self.type_of_contingency = type_of_contingency

    def check_all_details_gathered(self):

        if self.type_of_contingency is None:
            return False
        else:
            if self.type_of_contingency is "blockage":
                if self.location_one is None or self.location_two is None or self.type_of_blockage is None:
                    return False
                else:
                    return True
            elif self.type_of_contingency is "weather":
                return True
            elif self.type_of_contingency is "short_form":
                if self.location_one is None or self.location_two is None or self.time_of_incident is None:
                    return False
                else:
                    return True

    def check_what_info_missing(self):
        if self.location_one is None or self.location_two is None:
            return "location"
        if self.type_of_blockage is None:
            return "blockage"
        # if self.time_of_incident is None:
        #     return "blockage_time"
        # if self.type_of_contingency is None:
        #     return "contingency_type"

        return None

    def remove_all_info(self):
        self.location_one = None
        self.location_two = None
        self.time_of_incident = None
        self.type_of_blockage = None
        self.type_of_contingency = None

