import scrapy
import items
from scrapy_playwright.page import PageMethod

#https://www.lner.co.uk/buy-tickets/booking-engine/?ocrs=NRW&dcrs=KGX&outy=2025&outm=05&outd=16&outh=13&outmi=45&JourneyType=returnJourney&rety=2025&retm=05&retd=31&reth=15&retmi=45&nad=2&nch=1&rc=YNG%2CTST%2C&rcn=1%2C1

class LNERSpider(scrapy.Spider):
	name = 'LNER'

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
			self.url = (f"https://www.lner.co.uk/buy-tickets/booking-engine/?"
					f"ocrs={self.origin}"
					f"&dcrs={self.destination}"
					f"&outy={self.leavingYear}"
					f"&outm={self.leavingMonth}"
					f"&outd={self.leavingDay}"
					f"&outh={self.leavingHour}"
					f"&outmi={self.leavingMin}"
					f"&JourneyType={self.ticket_type}Journey"
					f"&rety={self.returnYear}"
					f"&retm={self.returnMonth}"
					f"&retd={self.returnDay}"
					f"&reth={self.returnHour}"
					f"&retmi={self.returnMin}"
					f"&nad={self.adults}"
					f"&nch={self.children}"

					f"&leavingType={self.leavingType}"
					f"&returnType={self.returnType}"
					)
			if len(self.railcards) != 0:
				self.url += "&rc="
				for i in range(len(self.railcards)):
					for j in range(len(self.railcards[i])):
						self.url += str(self.railcards[i][0]) + "%2C"
				self.url += "&rcn="
				for i in range(len(self.railcards)):
					self.url += str(self.railcards[i][1]) + "%2C"
			if self.leavingType == "arriving":
				self.url += "&outda=n"
			else:
				self.url += "&outda=y"
			if self.returnType == "arriving":
				self.url += "&retda=n"
			else:
				self.url += "&retda=y"
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
			if self.leavingType == "arriving":
				self.url += "&outda=n"
			else:
				self.url += "&outda=y"
			if self.returnType == "arriving":
				self.url += "&retda=n"
			else:
				self.url += "&retda=y"
			self.url += "&extraTime=0#O"

	@classmethod
	def update_settings(cls, settings):
		super().update_settings(settings)
		settings.set("BOT_NAME", "lner_spider", priority="spider")
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
		for ticket in response.css(''):
			ticket_field = items.TicketItem()
#			ticket_field['duration'] = ticket.css('div > div > button > p > time > span::text').get()[0:-2]
#			ticket_field['changeovers'] = ticket.css('div > div > div > button > p > span:last-of-type::text').get()
#			ticket_field['price'] = float(ticket.css('div > div > div > div > div > span:last-of-type::text').get()[1::])
#			ticket_field['leaveTime'] = ticket.css('div > div > span > time::text').get()
#			ticket_field['ticketType'] = self.ticket_type
#			ticket_field['origin'] = self.origin
#			ticket_field['destination'] = self.destination
#			ticket_field['leaveDate'] = self.leavingDay +  "/" + self.leavingMonth + "/" + self.leavingYear
#			ticket_field['adults'] = self.adults
#			ticket_field['children'] = self.children
#			ticket_field['railcards'] = self.railcards
#			ticket_field['url'] = self.url
			ticket_field['duration'] = "success"
			ticket_field['changeovers'] = "success"
			ticket_field['price'] = "success"
			ticket_field['leaveTime'] = "success"
			ticket_field['ticketType'] = "success"
			ticket_field['origin'] = "success"
			ticket_field['destination'] = "success"
			ticket_field['leaveDate'] = "success"
			ticket_field['adults'] = "success"
			ticket_field['children'] = "success"
			ticket_field['railcards'] = "success"
			ticket_field['url'] = "success"
			yield ticket_field
