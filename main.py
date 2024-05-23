"""Process that extracts fresh news from a news website."""
from RPA.Browser.Selenium import Selenium
from datetime import datetime, timedelta
import time
import pandas as pd
from base import log


class LATimesScraper:
    def __init__(self, search_phrase, topic, number_of_months):
        self.browser = Selenium()
        self.url_website = "https://www.latimes.com/"
        self.search_phrase = search_phrase
        self.topic = topic
        self.number_of_months = number_of_months
        self.articles_data = []

    def open_website(self):
        log.info("Opening website")
        self.browser.open_available_browser(self.url_website)

    def search_for_phrase(self):
        log.info(f"Searching for phrase: {self.search_phrase}")
        self.browser.click_element(
            "xpath://button[@data-element='search-button']")
        self.browser.wait_until_element_is_visible(
            "xpath://input[@data-element='search-form-input']",
            timeout=10)
        self.browser.input_text(
            "xpath://input[@data-element='search-form-input']",
            self.search_phrase)
        self.browser.press_keys(
            "xpath://input[@data-element='search-form-input']",
            "\uE007")
        self.browser.wait_until_page_contains("Search results", timeout=10)

    def select_topic_checkbox(self):
        log.info(f"Selecting topic checkbox for: {self.topic}")
        label_xpath = f"//label[contains(., '{self.topic}')]"
        if self.browser.is_element_visible(label_xpath):
            checkbox_input_xpath = f"{label_xpath}//input[@type='checkbox']"
            self.browser.select_checkbox(checkbox_input_xpath)
        else:
            log.warning(f"Checkbox for topic '{self.topic}' not found.")

    def select_newest_option(self):
        log.info("Selecting 'Newest' option from dropdown.")
        self.browser.wait_until_element_is_visible(
            "xpath://select[@name='s']", timeout=10)
        select_element_xpath = "//select[@name='s']"
        self.browser.select_from_list_by_value(select_element_xpath, "1")

    def is_article_within_date_range(self, article_date):
        """Check if the article date is within the specified dates."""
        today = datetime.today()
        start_date = today - timedelta(days=self.number_of_months * 30)
        return start_date <= article_date <= today

    def scrape_news_articles(self):
        """Scrape news articles on the current page."""
        log.info("Scraping news articles on the current page.")
        self.browser.wait_until_element_is_visible(
            "xpath=//li/ps-promo", timeout=10)
        articles = self.browser.get_webelements("xpath=//li/ps-promo")
        for article in articles:
            title = article.find_element(
                "xpath", ".//h3[@class='promo-title']/a").text
            link = article.find_element(
                "xpath", ".//h3[@class='promo-title']/a").get_attribute("href")
            description = article.find_element(
                "xpath", ".//p[@class='promo-description']").text
            date_str = article.find_element(
                "xpath", ".//p[@class='promo-timestamp']").text
            article_date = self.parse_article_date(date_str)
            image_src = article.find_element(
                "xpath", ".//picture/img").get_attribute("src")
            image_filename = image_src.split('/')[-1] if image_src else ""

            if not self.is_article_within_date_range(article_date):
                log.info("News is out of the date range. Stopping scraping.")
                return False

            self.articles_data.append({
                "Title": title,
                "Link": link,
                "Description": description,
                "Date": article_date.strftime('%Y-%m-%d'),
                "Image Filename": image_filename
            })
            log.info(f"Scraped article: {title}")

        return True

    def parse_article_date(self, date_str):
        """Parse the article date from the given date string."""
        try:
            article_date = datetime.strptime(date_str, "%B %d, %Y")  # Adj
        except ValueError:
            # Fallback for other possible date formats
            article_date = datetime.today()
        return article_date

    def navigate_to_next_page(self):
        """Navigate to the next page if available."""
        next_page_button_xpath = "//div[@class='search-results-module-next-page']/a"
        if self.browser.is_element_visible(next_page_button_xpath):
            self.browser.click_element(next_page_button_xpath)
            time.sleep(5)  # Wait for the next page to load
            return True
        return False

    def save_to_excel(self, file_name):
        """Save the scraped data to an Excel file."""
        df = pd.DataFrame(self.articles_data)
        df.to_excel(file_name, index=False)

    def run(self):
        self.open_website()
        self.search_for_phrase()
        self.select_topic_checkbox()
        self.select_newest_option()
        self.scrape_news_articles()
        # while True:
        #     if not self.scrape_news_articles():
        #         break
            # if not self.navigate_to_next_page():
            #     break
        self.browser.close_all_browsers()
        self.save_to_excel("scraped_news.xlsx")


if __name__ == "__main__":
    search_phrase = "climate change"
    topic = "California"
    number_of_months = 1  # Example: current and previous month
    scraper = LATimesScraper(search_phrase, topic, number_of_months)
    scraper.run()
