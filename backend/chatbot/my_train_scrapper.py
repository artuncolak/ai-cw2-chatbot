from selenium import webdriver
from selenium.webdriver.common.by import By
import scrapy
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod
import re

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
			ticket_field = TicketItem()
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

class NationalRailScraper:

    def __init__(self):
        self.url=''

    def run_scrapper(self, ticket_type="single", source=None, destination=None,
                     leaving_type="DepartingAt", leaving_date_time=None, returning_type=None,
                     return_date_time=None, adults=1, children=0, railcards=[]):
        ticket_planner = {}
        if ticket_type == "oneWay":
            ticket_planner['ticket_type'] = "single"
        elif ticket_type == "Return":
            ticket_planner['ticket_type'] = "return"
        ticket_planner['source'] = source
        ticket_planner['destination'] = destination
        if leaving_type == "DepartingAt":
            ticket_planner['leaving_type'] = "departing"
        elif leaving_type == "ArrivingBefore":
            ticket_planner['leaving_type'] = "arriving"
        ticket_planner['leaving_date_time'] = leaving_date_time
        if returning_type == "DepartingAt":
            ticket_planner['returning_type'] = "departing"
        elif returning_type == "ArrivingBefore":
            ticket_planner['returning_type'] = "arriving"
        ticket_planner['return_date_time'] = return_date_time
        ticket_planner['adults'] = adults
        ticket_planner['children'] = children
        ticket_planner['railcards'] = railcards
        print(ticket_planner)

        results = []

        def crawler_results(signal, sender, item, response, spider):
            results.append(item)

        dispatcher.connect(crawler_results, signal=signals.item_scraped)
        
        process = CrawlerProcess()
        if ticket_planner['ticket_type'] == "return":
            process.crawl(NationalRailSpider,
                ticket_type=ticket_planner['ticket_type'],
                origin=ticket_planner['source'],
                destination=ticket_planner['destination'],
                leavingType=ticket_planner['leaving_type'],
                leavingYear=ticket_planner['leaving_date_time'][0:4],
                leavingMonth=ticket_planner['leaving_date_time'][5:7],
                leavingDay=ticket_planner['leaving_date_time'][8:10],
                leavingHour=ticket_planner['leaving_date_time'][11:13],
                leavingMin=ticket_planner['leaving_date_time'][14:16],
                returnType=ticket_planner['returning_type'],
                returnYear=ticket_planner['return_date_time'][0:4],
                returnMonth=ticket_planner['return_date_time'][5:7],
                returnDay=ticket_planner['return_date_time'][8:10],
                returnHour=ticket_planner['return_date_time'][11:13],
                returnMin=ticket_planner['return_date_time'][14:16],
                adults=ticket_planner['adults'],
                children=ticket_planner['children'],
                railcards=ticket_planner['railcards'],
                )
        elif  ticket_planner['ticket_type'] == "single":
            process.crawl(NationalRailSpider,
                ticket_type=ticket_planner['ticket_type'],
                origin=ticket_planner['source'],
                destination=ticket_planner['destination'],
                leavingType=ticket_planner['leaving_type'],
                leavingYear=ticket_planner['leaving_date_time'][0:4],
                leavingMonth=ticket_planner['leaving_date_time'][5:7],
                leavingDay=ticket_planner['leaving_date_time'][8:10],
                leavingHour=ticket_planner['leaving_date_time'][11:13],
                leavingMin=ticket_planner['leaving_date_time'][14:16],
                returnType=None,
                returnYear=None,
                returnMonth=None,
                returnDay=None,
                returnHour=None,
                returnMin=None,
                adults=ticket_planner['adults'],
                children=ticket_planner['children'],
                railcards=ticket_planner['railcards'],
                )

        process.start()  # the script will block here until the crawling is finished
        return results

class MyTrainScrapper:

    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless=new')

        self.driver = webdriver.Chrome(options=self.options)
        self.url = ''


    def run_scrapper(self, ticket_type="oneWay", source=None, destination=None,
                     leaving_type="DepartingAt", leaving_date_time=None, returning_type=None,
                     return_date_time=None, adults=1, children=0, railcards=[]):
        self.ticket_type = ticket_type
        self.source = source
        self.destination = destination
        self.leaving_type = leaving_type
        self.leaving_date_time = leaving_date_time
        self.returning_type = returning_type
        self.return_date_time = return_date_time
        self.adults = adults
        self.children = children
        self.railcards = railcards

        if source == None:
            raise ValueError("You must specify a source station")
        elif destination == None:
            raise ValueError("You must specify a destination station")
        elif leaving_date_time == None:
            raise ValueError("You must specify a leaving date and time")

#        ticket_planner = {
#            "source": source,
#            "destination": destination,
#            "adults": 1,
#            "journeyType": ["oneWay"],
#            "outboundDate": leaving_date_time,
#            "outboundTimeType": ["DepartingAt","ArrivingBefore"],
#            "viaAvoid": "Via"
#        }

        self.url = (f"https://buy.mytrainticket.co.uk/results?from={self.source}"
                               f"&to={self.destination}"
                               f"&adults={self.adults}&children={self.children}"
                               f"&journeyType={self.ticket_type}"
                               f"&outboundDate={self.leaving_date_time}"
                               f"&outboundTimeType={self.leaving_type}")
        if returning_type:
            self.url += "&returnDate=" + str(self.return_date_time)
            self.url += "&returnTimeType=" + str(self.returning_type)
        if len(self.railcards) == 1:
            self.url += "&railcard=" + str(self.railcards[0][0]) + "&railcardQuantity=" + str(self.railcards[0][1])
        elif len(self.railcards) > 1:
            raise ValueError("MyTrainticket can only handle one type of railcard at a time")
#        self.url = "https://buy.mytrainticket.co.uk/results?from=2d7a7a24-6514-4bc5-bf83-ddcba5be0448&to=85b48392-83cf-4bea-9a80-17c8189b1c06&adults=1&children=0&journeyType=OneWay&outboundDate=2025-06-01T07:00:00Z&outboundTimeType=DepartingAt&viaAvoid=Via"
#        self.url = "https://buy.mytrainticket.co.uk/results?from=2d7a7a24-6514-4bc5-bf83-ddcba5be0448&to=85b48392-83cf-4bea-9a80-17c8189b1c06&adults=1&children=0&journeyType=Return&outboundDate=2025-06-14T07:00:00Z&outboundTimeType=DepartingAt&returnDate=2025-06-15T08:00:00Z&returnTimeType=DepartingAt&viaAvoid=Via"
#        print(self.url)

        self.driver.get(self.url)

        ticketinfo = self.scrapper()

        self.driver.quit()
        return ticketinfo

    def scrapper(self):
        tickets = self.driver.find_elements(By.CLASS_NAME, 'journey')

        scraped_tickets = []

        for ticket in tickets:
            current_ticket = {}

#            timee = ticket.find_elements(By.CLASS_NAME,'journey-time')
#            timsd = ticket.find_elements(By.XPATH,"//div[@class='journey-start']/div[@class='out-time-wrapper']/p[1]")
#
#            for kls in timsd:
#                print('timsd',kls.text)
#
#            for kk in timee:
#                print(kk.text)

            prices = ticket.find_elements(By.CLASS_NAME,'standard-fare-selection')
            #print('price',len(price))
            for price in prices:

#                print(".".join(re.findall("\d+", jj.text)[0:2]))
                current_ticket['price'] = float(".".join(re.findall("\d+", price.text)[0:2]))

            durations = ticket.find_elements(By.CLASS_NAME,'journey-meta')
            #print('duration',len(duration))

            for duration in durations:

#                print(th.text)
                if len(duration.text) > 0:
                    current_ticket['duration'], current_ticket['changeovers'] = duration.text.split(", ")

#            leave_times = ticket.find_elements(By.XPATH, "//div[@class='journey-start']/div[@class='out-time-wrapper']/p[1]")
#            for leave_time in leave_times:
#                if len(leave_time.text) > 0:
#                    current_ticket['leaveTime'] = leave_time.text

            
            current_ticket['ticketType'] = self.ticket_type
            current_ticket['origin'] = self.source
            current_ticket['destination'] = self.destination
            current_ticket['leaveDate'] = self.leaving_date_time[8:10] +  "/" + \
            self.leaving_date_time[5:7] + "/" + self.leaving_date_time[0:4]
            if self.returning_type:
                current_ticket['returnDate'] = self.return_date_time[8:10] +  "/" + \
                self.return_date_time[5:7] + "/" + self.return_date_time[0:4]
            current_ticket['adults'] = self.adults
            current_ticket['children'] = self.children
            current_ticket['railcards'] = self.railcards
            current_ticket['url'] = self.url

#            print(current_ticket)
            scraped_tickets.append(current_ticket)
#            print('---'*5)

        return scraped_tickets

