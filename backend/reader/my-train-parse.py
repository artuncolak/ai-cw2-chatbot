from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import random


def scrapper(driver):
    tickets = driver.find_elements(By.CLASS_NAME, 'journey')

    scraped_tickets = []
    # driver.execute_script("arguments[0].scrollIntoView(true);", tickets)
    # actions = chains(driver)


    print(len(tickets))
    prices = []
    cheapest_price = 0

    for ticket in tickets:
        # print(ticket.text)
        test = ""
        current_ticket = {}

        timee = ticket.find_elements(By.CLASS_NAME,'journey-time')
        # timee = ticket.find_elements(By.CLASS_NAME,'journey-time')

        timsd = ticket.find_elements(By.XPATH,"//div[@class='journey-start']/div[@class='out-time-wrapper']/p[1]")
        #
        for kls in timsd:
            print('timsd',kls.text)

        for kk in timee:
            print(kk.text)

        # current_ticket['source'] = timee[0].text
        # current_ticket['destination'] = timee[1].text



        price = ticket.find_elements(By.CLASS_NAME,'standard-fare-selection')
        print('price',len(price))
        for jj in price:

            print(jj.text)
            current_ticket['price'] = jj.text

        duration = ticket.find_elements(By.CLASS_NAME,'journey-meta')
        print('duration',len(duration))

        for th in duration:

            print(th.text)
            if len(th.text) > 0:
                current_ticket['duration'] = th.text


        cheapest = ticket.find_elements(By.CLASS_NAME,'cheapest-text')
        print('cheapest',len(cheapest))


        for kdk in cheapest:

            print(kdk.text)
            if len(kdk.text) > 0:
                current_ticket['cheapest_price'] = kdk.text
                cheapest_price = kdk.text

        # # timess = ticket.find_elements(By.TAG_NAME, 'span')
        # duration = ticket.find_elements(By.CLASS_NAME, '_1nsjd0ym')
        #
        # for ddur in duration:
        #     kj = ddur.find_elements(By.CLASS_NAME, '_e4x16a')
        #     for kk in kj:
        #         print(kk.text)
        #
        # gh = ticket.find_elements(By.TAG_NAME, 'ul')
        #
        # for t in gh:
        #     hj = t.find_elements(By.TAG_NAME, 'li')
        #
        #     for h in hj:
        #         print(h.text)

        # ppw = ticket.find_elements(By.TAG_NAME, 'p')
        #
        # print(len(ppw))
        # for o in ppw:
        #     print(o.text, len(o.text))

        # ttt = ticket.find_elements(By.TAG_NAME, 'time')
        #
        # for tt in ttt:
        #     print(tt.text)
        # #
        # for dur in duration:
        #     dff = dur.find_elements(By.XPATH("//div/div/div/p/time"))
        #
        #     for v in dff:
        #         print(v.text)

            # print(dur.text)
            # test += dur.text + ","

        # for times in timess:
            # print(times.text)
            # if len(times.text) > 0:

                # test += times.text + ","
            # scraped_tickets.append(times.text)
        # println(ticket.text)
        # print(timess.)
        # print(test)
        #
        # ActionChains(driver).move_to_element(ticket).perform()
        #
        # departure = ticket.find_elements(By.CSS_SELECTOR,"[data-test='departure-time-column']")
        # arrival = ticket.find_elements(By.CSS_SELECTOR,"[data-test='arrival-time-column']")
        # standard_price = ticket.find_elements(By.CSS_SELECTOR,"[data-test='alternative-price']")
        # duration = ticket.find_elements(By.CSS_SELECTOR,"[data-test='desktop-duration-and-changes']")
        #
        # price = ''
        # for j in departure:
        #     print(j.text)
        # for i in arrival:
        #     print(i.text)
        # for ik in standard_price:
        #     print('price',ik.text)
        #     price = ik.text
        #     prices.append(price)
        #     break
        # for kl in duration:
        #     print('duration',kl.text)
        # scraped_tickets.append({
        #     "departure": departure[0].text,
        #     "arrival": arrival[0].text,
        #     "standard_price": price ,
        #     # "first_price":standardPrice[1].text if standardPrice[1].text else "" ,
        #     # "duration": duration[0].text if duration[0].text else "" ,
        #
        # })
        print(current_ticket)
        scraped_tickets.append(current_ticket)
        print('---'*5)

    cheap = []
    # for ticket in scraped_tickets:
    #     print('ttt',ticket)
    #     if ticket['price'] == cheapest_price:
    #         cheap.append(ticket)

    # print(min(prices))
    print(cheap)


options = webdriver.ChromeOptions()

options.add_argument('--headless=new')

driver = webdriver.Chrome(options=options)

ticket_planner = {
    "source": "2d7a7a24-6514-4bc5-bf83-ddcba5be0448",
    "destination": "dcb95f85-b7e6-4615-8531-3e206b319e0b",
    "adults": 1,
    "journeyType": ["oneWay"],
    "outboundDate": "2025-05-16T06:00:00Z",
    "outboundTimeType": ["DepartingAt"],
    "viaAvoid":"Via"


}

my_train_ticket_url = (f"https://buy.mytrainticket.co.uk/results?from={ticket_planner['source']}"
                       f"&to={ticket_planner['destination']}"
                       f"&adults={ticket_planner['adults']}&children=0"
                       f"&journeyType={ticket_planner['journeyType'][0]}"
                       f"&outboundDate={ticket_planner['outboundDate']}"
                       f"&outboundTimeType={ticket_planner['outboundTimeType'][0]}"
                       f"&viaAvoid={ticket_planner['viaAvoid']}")

print(my_train_ticket_url)
driver.get(my_train_ticket_url)

# print(driver.page_source)


scrapper(driver)

driver.quit()
