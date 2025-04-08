import scrapy


class TicketItem(scrapy.Item):
    duration = scrapy.Field()
    changeovers = scrapy.Field()
    price = scrapy.Field()
    leaveTime = scrapy.Field()
