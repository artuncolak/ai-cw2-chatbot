# ISSUES DOWNLOADING WEBPAGE: ACCESSING DYNAMIC ELEMENTS

import scrapy
from scrapy_playwright.page import PageMethod
from train_ticket_scraper.items import TicketItem

class TrainSplitSpider(scrapy.Spider):
	name = 'trainsplit'

	def start_requests(self):
		url = "https://trainsplit.com/results?FromStation=7073090&ToStation=7061210&Adults=1&OutboundDate=15%2F04%2F2025&OutboundTime=16%3A15&InboundDate=15%2F04%2F2025&InboundTime=18%3A15&UseSplits=0&Railcard=YNG&searchBy=0&firstClass=false&flexible=false&selectionMethod=Grid"
		yield scrapy.Request(url=url,
            meta={
            'playwright': True,
            'playwright_page_methods': [
                PageMethod("wait_for_load_state", "domcontentloaded"),
                PageMethod("wait_for_load_state", "networkidle"),
                ]
            })

	def parse(self, response):
		for ticket in response.css('div.container > div.search-results > div.card > div.card-body > div.tab-content > div.tab-pane > div.class-grid-enclosure > div.grid-outer-container > div.grid-container'):
			ticket_field = TicketItem()
#			ticket_field['duration'] = ticket.css('div > div > button > p > time > span::text').get()[0:-2]
#			ticket_field['changeovers'] = ticket.css('div > div > div > button > p > span:last-of-type::text').get()
#			ticket_field['price'] = ticket.css('div > span::text').get()[1::]
#			ticket_field['leaveTime'] = ticket.css('div > div > span > time::text').get()
			ticket_field['duration'] = "success"
			ticket_field['changeovers'] = "success"
			ticket_field['price'] = "success"
			ticket_field['leaveTime'] = "success"

			yield ticket_field
