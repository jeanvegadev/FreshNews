"""Process that obtains the lastest news from a news website."""
from RPA.Browser.Selenium import Selenium

browser = Selenium()

url_website = "https://www.latimes.com/"
browser.open_available_browser(url_website)
# Search term
search_term = "climate change"



browser.close_all_browsers()
