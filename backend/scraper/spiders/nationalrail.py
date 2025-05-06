import scrapy
import items
from scrapy_playwright.page import PageMethod

class NationalRailSpider(scrapy.Spider):
	name = 'nationalrail'

	def __init__(self, ticket_type, origin, destination,
			  leavingType, leavingYear, leavingMonth,
			  leavingDay, leavingHour, leavingMin,
			  returnType, returnYear, returnMonth,
			  returnDay, returnHour, returnMin,
			  adults, children, railcards):
		self.ticket_type = ticket_type
		self.origin = origin
		self.destination = destination
		self.leavingType = leavingType
		self.leavingYear = leavingYear
		self.leavingMonth = leavingMonth
		self.leavingDay = leavingDay
		self.leavingHour = leavingHour
		self.leavingMin = leavingMin
		self.returnType = returnType
		self.returnYear = returnYear
		self.returnMonth = returnMonth
		self.returnDay = returnDay
		self.returnHour = returnHour
		self.returnMin = returnMin
		self.adults = adults
		self.children = children
		self.railcards = railcards

		if ticket_type == "return":
			self.url = (f"https://www.nationalrail.co.uk/journey-planner/?type={self.ticket_type}"
					f"&origin={self.origin}"
					f"&destination={self.destination}"
					f"&leavingType={self.leavingType}"
					f"&leavingDate={self.leavingDay}{self.leavingMonth}{self.leavingYear[2:]}"
					f"&leavingHour={self.leavingHour}"
					f"&leavingMin={self.leavingMin}"
					f"&returnType={self.returnType}"
					f"&returnDate={self.returnDay}{self.returnMonth}{self.returnYear[2:]}"
					f"&returnHour={self.returnHour}"
					f"&returnMin={self.returnMin}"
					f"&adults={self.adults}"
					f"&children={self.children}")
			for i in range(len(railcards)):
				self.url += "&railcards=" + str(self.railcards[i][0]) + "%7C" + str(self.railcards[i][1])
			self.url += "&extraTime=0#O"
		else:
			self.url = (f"https://www.nationalrail.co.uk/journey-planner/?type={self.ticket_type}"
					f"&origin={self.origin}"
					f"&destination={self.destination}"
					f"&leavingType={self.leavingType}"
					f"&leavingDate={self.leavingDay}{self.leavingMonth}{self.leavingYear[2:]}"
					f"&leavingHour={self.leavingHour}"
					f"&leavingMin={self.leavingMin}"
					f"&adults={self.adults}"
					f"&children={self.children}")
			for i in range(len(railcards)):
				self.url += "&railcards=" + str(self.railcards[i][0]) + "%7C" + str(self.railcards[i][1])
			self.url += "&extraTime=0#O"

	@classmethod
	def update_settings(cls, settings):
		super().update_settings(settings)
		settings.set("BOT_NAME", "nationalrail_spider", priority="spider")
		settings.set("ROBOTSTXT_OBEY", False, priority="spider")
		settings.set("CONCURRENT_REQUESTS", 32, priority="spider")
		settings.set("COOKIES_ENABLED", True, priority="spider")
		settings.set("DOWNLOAD_HANDLERS", { "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
		"https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler", }, priority="spider")
		settings.set("TWISTED_REACTOR", "twisted.internet.asyncioreactor.AsyncioSelectorReactor", priority="spider")

	def start_requests(self):
		yield scrapy.Request(url=self.url,
            meta={
            'playwright': True,
            'playwright_page_methods': [
                PageMethod("wait_for_load_state", "domcontentloaded"),
                PageMethod("wait_for_load_state", "networkidle"),
                ]
            })

	def parse(self, response):
		for ticket in response.css('fieldset > ul > li > section > div > div'):
			ticket_field = items.TicketItem()
			ticket_field['duration'] = ticket.css('div > div > button > p > time > span::text').get()[0:-2]
			ticket_field['changeovers'] = ticket.css('div > div > div > button > p > span:last-of-type::text').get()
			ticket_field['price'] = float(ticket.css('div > div > div > div > div > span:last-of-type::text').get()[1::])
			ticket_field['leaveTime'] = ticket.css('div > div > span > time::text').get()
			ticket_field['ticketType'] = self.ticket_type
			ticket_field['origin'] = self.origin
			ticket_field['destination'] = self.destination
			ticket_field['leaveDate'] = self.leavingDay +  "/" + self.leavingMonth + "/" + self.leavingYear
			ticket_field['adults'] = self.adults
			ticket_field['children'] = self.children
			ticket_field['railcards'] = self.railcards
			ticket_field['url'] = self.url
			yield ticket_field
