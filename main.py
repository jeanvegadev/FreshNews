"""Process that obtains the lastest news from a news website."""
from RPA.Browser.Selenium import Selenium
import time

browser = Selenium()

url_website = "https://www.latimes.com/"
browser.open_available_browser(url_website)

# Locate and click the search button
browser.click_element("xpath://button[@data-element='search-button']")

# Optionally, wait for the text input to appear (adjust the timeout as needed)
browser.wait_until_element_is_visible(
    "xpath://input[@data-element='search-form-input']",
    timeout=10)

# Define the search term
search_term = "climate change"

# Locate the newly appeared text input field and enter the search term
browser.input_text("xpath://input[@data-element='search-form-input']",
                   search_term)

# Pressing Enter
browser.press_keys(
    "xpath://input[@data-element='search-form-input']",
    "\uE007")

# Optionally, wait for the results to load (adjust the timeout as needed)
browser.wait_until_page_contains("Results", timeout=10)


# Define the topic to check
topic = "California"

# Locate the label that matches the topic
label_xpath = f"//label[contains(., '{topic}')]"

# Verify if the label is found and then check the associated checkbox
if browser.is_element_visible(label_xpath):
    # Find the associated checkbox input and check it
    checkbox_input_xpath = f"{label_xpath}//input[@type='checkbox']"
    browser.select_checkbox(checkbox_input_xpath)

# Select the option that shows the newest news
select_element_xpath = "//select[@name='s']"
browser.select_from_list_by_value(select_element_xpath, "1")

time.sleep(5)
browser.close_all_browsers()
