import scrapy

class TicketItem(scrapy.Item):
	duration = scrapy.Field()
	changeovers = scrapy.Field()
	price = scrapy.Field()
	leaveTime = scrapy.Field()
	ticketType = scrapy.Field()
	origin = scrapy.Field()
	destination = scrapy.Field()
	leaveDate = scrapy.Field()
	adults = scrapy.Field()
	children = scrapy.Field()
	railcards = scrapy.Field()
	url = scrapy.Field()
