import scrapy
from scrapy_playwright.page import PageMethod
from train_ticket_scraper.items import TicketItem

class NationalRailSpider(scrapy.Spider):
	name = 'nationalrail'

	def start_requests(self):
		url = "https://www.nationalrail.co.uk/journey-planner/?type=single&origin=NRW&destination=KGX&leavingType=departing&leavingDate=150425&leavingHour=14&leavingMin=00&adults=1&railcards=YNG%7C1#O"
        # type = ["single","return"]
        # note not open return
        # origin, destination = [...]
        # leavingType, returnType = [
            # "departing" = Departing after
            # "arriving" = Arriving by
            # "first" = First train
            # "last" = Last train
            # ]
        # leavingDate, leavingHour, leavingMin
        # returnDate, returnHour, returnMin
        # adults = 1 to 9
        # children = 1 to 9
        # 1 <= adults + children <= 9
        # railcards = [
            # "TSU" = 16-17 Saver
            # "YNG" = 16-25 Railcard
            # "W18" = 18 Saver Transport for Wales
            # "TST" = 26-30 Railcard
            # "NGC" = Annual Gold Card | Gold Record Card
            # "CRC" = Cambrian Railcard
            # "OC5" = Club 50 Web: ScotRail
            # "DRD" = Dales Railcard
            # "DCG" = Devon & Cornwall Gold Card
            # "DCR" = Devon & Cornwall Railcard
            # "DIS" = Disabled Persons Railcard
            # "EVC" = Esk Valley Railcard
            # "FAM" = Family & Friends Railcard
            # "GS3" = GroupSave
            # "HOW" = Heart of Wales Railcard
            # "HRC" = Highland Railcard
            # "HMF" = HM Forces Railcard
            # "JCP" = Jobcentre Plus Travel Discount Card
            # "CUR" = MyCumbria Card
            # "NEW" = Network Railcard
            # "HCC" = North Lincolnshire Concessionary 34%
            # "HCS" = North Lincolnshire Concessionary 50%
            # "PBR" = Pembrokeshire Railcrd
            # "RRC" = Rhondda Railcard
            # "SRN" = Senior Railcard
            # "SSP" = South Yorkshire 16-18 Zoom Travel Pass
            # "WSC" = Student Railcard: Transport for Wales
            # "2TR" = Two Together Railcard
            # "VLS" = Valleys Senior Railcard
            # "VLC" = Valleys Student Railcard
            # "VET" = Veterans Railcard
            # "WYD" = West Yorkshire Disables Concessionary Discount
            # "WMR" = West Yorkshire MetroRover Permit
            # "WYS" = West Yorkshire Senior Concessionary Discount
            # ]|number
        # via = [...]
        # viaType = ["via","avoid","change-at","do-not-change-at"]
        # finish query with "#O"
		yield scrapy.Request(url=url,
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
			ticket_field['price'] = ticket.css('div > div > div > div > div > span:last-of-type::text').get()[1::]
			ticket_field['leaveTime'] = ticket.css('div > div > span > time::text').get()

			yield ticket_field
