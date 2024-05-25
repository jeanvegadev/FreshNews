"""Process that extracts fresh news from a news website."""
from RPA.Browser.Selenium import Selenium
from datetime import datetime
import time
import pandas as pd
from base import log
import os
import urllib.request
import re


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
            time.sleep(5)
        else:
            log.warning(f"Checkbox for topic '{self.topic}' not found.")

    def select_newest_option(self):
        log.info("Selecting 'Newest' option from dropdown.")
        self.browser.wait_until_element_is_visible(
            "xpath://select[@name='s']", timeout=10)
        select_element_xpath = "//select[@name='s']"
        self.browser.select_from_list_by_value(select_element_xpath, "1")
        time.sleep(10)

    def is_article_within_date_range(self, article_date):
        """Check if the article date is within the specified dates."""
        today = datetime.today()
        if self.number_of_months == 0:
            start_date = datetime(today.year, today.month, 1)
        else:
            start_date = datetime(today.year,
                                  today.month - number_of_months + 1,
                                  1)
        return start_date <= article_date

    def download_image(self, img_url, save_path):
        """Download image from URL and save to the specified path."""
        try:
            urllib.request.urlretrieve(img_url, save_path)
            log.info(f"Image saved to {save_path}")
        except Exception as e:
            log.error(f"Failed to save image: {e}")

    def scrape_news_articles(self):
        """Scrape news articles on the current page."""
        log.info("Scraping news articles on the current page.")
        self.browser.wait_until_element_is_visible(
            "xpath=//li/ps-promo", timeout=10)
        articles = self.browser.get_webelements("xpath=//li/ps-promo")
        for article in articles:
            title = article.find_element(
                "xpath", ".//h3/a").text
            date_str = article.find_element(
                "xpath", "./div/div[2]/p[2]").text
            description = article.find_element(
                "xpath", "./div/div[2]/p[1]").text
            article_date = self.parse_article_date(date_str)
            image_src = article.find_element(
                "xpath", ".//picture/img").get_attribute("src")
            image_filename = image_src.split('/')[-1] if image_src else ""
            image_filename = image_filename.split('%2F')[-1]
            if image_filename.lower()[-3:] not in ("jpg", "png"):
                image_filename = image_filename + ".jpg"

            if not self.is_article_within_date_range(article_date):
                log.info("News is out of the date range. Stopping scraping.")
                return False

            if image_src:
                image_path = os.path.join('images', image_filename)
                self.download_image(image_src, image_path)

            self.articles_data.append({
                "Title": title,
                "Date": article_date.strftime('%Y-%m-%d'),
                "Description": description,
                "Picture Filename": image_filename
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
        next_page_button_xpath = "//main/div[2]/div[3]"
        if self.browser.is_element_visible(next_page_button_xpath):
            self.browser.click_element(next_page_button_xpath)
            time.sleep(5)  # Wait for the next page to load
            return True
        return False

    def count_search_term_occurrences(self, row):
        """Count occurrences of the search term in both
        the title and description."""
        title_count = row['Title'].lower().count(self.search_phrase)
        description_count = row['Description'].lower().count(
                                                self.search_phrase)
        return title_count + description_count

    def contains_money_format(self, row):
        """Check if the title or description contains any amount
        of money in various formats."""
        money_patterns = [
            r'\$\d+(\.\d{1,2})?',  # $11.1 or $111,111.11
            r'\$\d{1,3}(,\d{3})*(\.\d{1,2})?',  # $111,111.11
            r'\d+ dollars',  # 11 dollars
            r'\d+ USD'  # 11 USD
        ]
        combined_text = f"{row['Title']} {row['Description']}".lower()
        for pattern in money_patterns:
            if re.search(pattern, combined_text):
                return True
        return False

    def save_to_excel(self, file_name):
        """Save the scraped data to an Excel file."""
        df = pd.DataFrame(self.articles_data)
        df['Search Phrases Count'] = df.apply(
                                        self.count_search_term_occurrences,
                                        axis=1)

        df['Contains Money Format'] = df.apply(
                                        self.contains_money_format,
                                        axis=1)
        df.to_excel(file_name, index=False)

    def run(self):
        self.open_website()
        self.search_for_phrase()
        self.select_topic_checkbox()
        self.select_newest_option()
        while True:
            if not self.scrape_news_articles():
                break
            if not self.navigate_to_next_page():
                break
        self.browser.close_all_browsers()
        self.save_to_excel("scraped_news.xlsx")


if __name__ == "__main__":
    search_phrase = "climate change"
    topic = "California"
    number_of_months = 1  # Example
    scraper = LATimesScraper(search_phrase, topic, number_of_months)
    scraper.run()
