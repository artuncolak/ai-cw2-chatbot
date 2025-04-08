# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NationalRailJsScraperPipeline:
    def process_item(self, item, spider):
        return item
