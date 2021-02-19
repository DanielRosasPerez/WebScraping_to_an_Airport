import re, random
from time import sleep
# SELENIUM:
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# SCRAPY:
from scrapy.item import Item
from scrapy.item import Field
from scrapy.spiders import CrawlSpider
from scrapy.loader import ItemLoader
from bs4 import BeautifulSoup

# Let's define our class where we'll save the data we want:
class Flight(Item):

    Company = Field(output_processor = lambda x: x[0])
    Flight_ID = Field(output_processor = lambda x: x[0])
    From = Field(output_processor = lambda x: x[0])
    To = Field(output_processor = lambda x: x[0])
    Flight_DEPARTURE_Times = Field(output_processor = lambda x: x[0])
    DEPARTURE_Time_Zone = Field(output_processor=lambda x: x[0])
    Scheduled_DEPARTURE_Hour = Field(output_processor = lambda x: x[0])
    Real_DEPARTURE_Hour = Field(output_processor = lambda x: x[0])
    Flight_ARRIVAL_Times = Field(output_processor = lambda x: x[0])
    ARRIVAL_Time_Zone = Field(output_processor=lambda x: x[0])
    Scheduled_ARRIVAL_Hour = Field(output_processor = lambda x: x[0])
    Real_ARRIVAL_Hour = Field(output_processor = lambda x: x[0])

# It's time to define our crawl spider:
class FlightsCrawlerSpider(CrawlSpider):

    name = "FlightsCrawlerSpider"
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/84.0.2",
        "FEED_EXPORT_ENCODING": "utf-8",
    }
    allowed_domains = ["flightstats.com"]
    # In "start_urls" INSERT THE URL FROM THE FLIGHT DESIRED THAT YOU WANT TO EXTRACT:
    start_urls = [
        "https://www.flightstats.com/v2/flight-tracker/departures/MEX/?year=2021&month=2&date=6&hour=0"
        #"https://www.flightstats.com/v2/flight-tracker/departures/MEX/?year=2021&month=2&date=7&hour=0"
    ] # IF YOU WISH YOU CAN UNCOMMENT THE LINK ABOVE (OR ADD ANOTHER ONE), AND SEE THAT THIS SCRIPT WORKS :)

    def creating_driver(self, url):

        opts = Options()
        ua = "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/\
                88.0.4324.96 Chrome/88.0.4324.96 Safari/537.36"
        opts.add_argument(ua)
        driver = webdriver.Chrome("./chromedriver.exe", options=opts)
        driver.get(url)
        return driver


    def parse_start_url(self, response):

        # SELENIUM:
        # Setting Main driver:
        main_driver = self.creating_driver(response.url)
        # LINKS TO EVERY HOUR IN THE DAY:
        hour_pages = [f"{response.url[:-1]}{i}" for i in [0, 6, 12, 18]]
        for hour_link in hour_pages:
            main_driver.get(hour_link)
            # LINKS TO EVERY PAGE IN THE PAGINATION:
            WebDriverWait(main_driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'table__Table')]/\
                a[not(contains(@class, 'table__TableHeaderContainer'))]"))
            )
            last_page = WebDriverWait(main_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'table__PaginationWrapper')]\
                //div[contains(@class, 'pagination__PageNavigationContainer')]/div[last()-2]/span"))
            )
            next_page_button = WebDriverWait(main_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'table__PaginationWrapper')]//\
                div[contains(@class, 'pagination__PageNavigationContainer')]/div[last()-1]"))
            )
            # Just in case we are not able to retrieve the maximum number of pages at the beginning:
            last_page = int(last_page.text.strip()) if last_page.text.isdigit() else 1000
            flag = True if last_page == 1000 else False

            # Let's dive into every page:
            pagination_clicks = 0
            while pagination_clicks < last_page:
                # LINKS TO EVERY FLIGHT IN EVERY PAGE OF PAGINATION:
                links = WebDriverWait(main_driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'table__Table')]/\
                    a[not(contains(@class, 'table__TableHeaderContainer'))]"))
                )
                links = [link.get_attribute("href") for link in links]
                driver = self.creating_driver(main_driver.current_url)
                for link in links:
                    try:
                        driver.get(link)
                        # ALGORITHM TO RETRIEVE DATA:
                        # Flight Data:
                        flight_data = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH,
                            "//div[contains(@class, 'ticket__FlightNumberContainer')]/div"))
                        )
                        flight_id, company = flight_data[0].text, flight_data[1].text
                        #############

                        from_to = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH,
                            "//div[contains(@class,'route-with-plane__RouteGroup')]//\
                            div[contains(@class,'text-helper__TextHelper') and \
                            not(contains(@class,'route-with-plane__AirportCodeLabel'))]"))
                        )
                        from_, to_ = from_to[0].text, from_to[1].text
                        #############

                        # Departure Data:
                        flight_departure_times = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ticket__TicketContent')]/\
                            div[1]/div[contains(@class, 'ticket__InfoSection')][last()]/div[last()]"))
                        )
                        flight_departure_times = flight_departure_times.text
                        #############
                        xpath_1 ="//div[contains(@class, 'ticket__TicketCard')][1]//\
                        div[contains(@class,'ticket__TimeGroupContainer')]/div[contains(@class, 'ticket__InfoSection')][1]/\
                        div[last()]/span"
                        xpath_2="//div[contains(@class, 'ticket__TicketCard')][1]//\
                        div[contains(@class,'ticket__TimeGroupContainer')]/div[contains(@class, 'ticket__InfoSection')]\
                        [last()]/div[last()]/span"
                        departure_time_zone = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, xpath_1))
                        )
                        if departure_time_zone.text == '':
                            departure_time_zone = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, xpath_2))
                            )
                        departure_time_zone = departure_time_zone.text.strip()

                        #############
                        scheduled_departure_hour = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ticket__TicketCard')][1]//\
                            div[contains(@class, 'ticket__TimeGroupContainer')]/\
                            div[contains(@class, 'ticket__InfoSection')][1]/div[last()]"))
                        )
                        hour_digit = ''
                        for i in filter(lambda x: x.isdigit() or x in [":","-"], scheduled_departure_hour .text):
                            hour_digit += i
                        scheduled_departure_hour = hour_digit.replace("--", "Unknown")

                        #############
                        real_departure_hour = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ticket__TicketCard')][1]//\
                            div[contains(@class,'ticket__TimeGroupContainer')]/div[contains(@class, 'ticket__InfoSection')]\
                            [last()]/div[last()]"))
                        )
                        hour_digit = ''
                        for i in filter(lambda x: x.isdigit() or x in [":","-"], real_departure_hour.text):
                            hour_digit += i
                        real_departure_hour = hour_digit.replace("--", "Unknown")
                        #############

                        # Arrival Data:
                        flight_arrival_times = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ticket__TicketContent')]\
                            /div[last()]/div[contains(@class, 'ticket__InfoSection')][last()]/div[last()]"))
                        )
                        flight_arrival_times = flight_arrival_times.text

                        #############
                        xpath_1 = "//div[contains(@class, 'ticket__TicketCard')][last()]//\
                        div[contains(@class,'ticket__TimeGroupContainer')]/div[contains(@class, 'ticket__InfoSection')][1]/\
                        div[last()]/span"
                        xpath_2 = "//div[contains(@class, 'ticket__TicketCard')][last()]//\
                        div[contains(@class,'ticket__TimeGroupContainer')]/div[contains(@class, 'ticket__InfoSection')]\
                        [last()]/div[last()]/span"
                        arrival_time_zone = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, xpath_1))
                        )
                        if arrival_time_zone.text == '':
                            arrival_time_zone = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, xpath_2))
                            )
                        arrival_time_zone = arrival_time_zone.text.strip()

                        #############
                        scheduled_arrival_hour = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ticket__TicketCard')]\
                            [last()]//div[contains(@class, 'ticket__TimeGroupContainer')]/\
                            div[contains(@class, 'ticket__InfoSection')][1]/div[last()]"))
                        )
                        hour_digit = ''
                        for i in filter(lambda x: x.isdigit() or x in [":","-"], scheduled_arrival_hour.text):
                            hour_digit += i
                        scheduled_arrival_hour = hour_digit.replace("--", "Unknown")

                        #############
                        real_arrival_hour = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ticket__TicketCard')]\
                            [last()]//div[contains(@class, 'ticket__TimeGroupContainer')]/\
                            div[contains(@class, 'ticket__InfoSection')][last()]/div[last()]"))
                        )
                        hour_digit = ''
                        for i in filter(lambda x: x.isdigit() or x in [":","-"], real_arrival_hour.text):
                            hour_digit += i
                        real_arrival_hour = hour_digit.replace("--", "Unknown")

                        # SAVING DATA:
                        item = ItemLoader(Flight(), driver.page_source)
                        item.add_value("Company", company)
                        item.add_value("Flight_ID", flight_id)
                        item.add_value("From", from_)
                        item.add_value("To", to_)
                        item.add_value("Flight_DEPARTURE_Times", flight_departure_times)
                        item.add_value("DEPARTURE_Time_Zone", departure_time_zone)
                        item.add_value("Scheduled_DEPARTURE_Hour", scheduled_departure_hour)
                        item.add_value("Real_DEPARTURE_Hour", real_departure_hour)
                        item.add_value("Flight_ARRIVAL_Times", flight_arrival_times)
                        item.add_value("ARRIVAL_Time_Zone", arrival_time_zone)
                        item.add_value("Scheduled_ARRIVAL_Hour", scheduled_arrival_hour)
                        item.add_value("Real_ARRIVAL_Hour", real_arrival_hour)

                        yield item.load_item()

                        print("#"*60)

                    except Exception as e:
                        print("¡Something went wrong with this flight!. The error is the following:")
                        print(e)
                        print("Let's try with the next flight.")

                driver.close() # We finish every session per page in pagination once we've retrieved the data.

                if flag:
                    # Just in case the maximum number of pages doesn't appear at the beginning because of the high
                    # number of pages. We will find it until it appears, that's why we have assigned "last_page"==1000,
                    # to be sure that we will arrive to the maximum number of existing pages. Once we retrieve it, we
                    # won't enter to this "if" again.
                    last_page = WebDriverWait(main_driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'table__PaginationWrapper')]\
                                    //div[contains(@class, 'pagination__PageNavigationContainer')]/div[last()-2]/span"))
                    )
                    last_page = int(last_page.text.strip()) if last_page.text.isdigit() else 1000
                    flag = True if last_page == 1000 else False

                next_page_button.click()
                pagination_clicks += 1

        main_driver.close() # Once we've finished to extract the data from the respective day. We finish the main session.
