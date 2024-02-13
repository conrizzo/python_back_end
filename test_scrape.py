# not relevant to the back-end but using for webscraping to test pre-rendering

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def fetch_headline(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    headline_element = soup.find('h1')
    if headline_element is not None:
        headline = headline_element.text
    else:
        headline = "No headline found"
    return headline

def fetch_page(url):
    driver = webdriver.Firefox()  # or webdriver.Chrome(), depending on your browser
    driver.get(url)

    # Wait up to 10 seconds for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'app')))
    # Wait an additional 5 seconds for the content within the div to load
    time.sleep(5)

    html = driver.page_source
    driver.quit()
    return html

page = fetch_page('https://conradswebsite.com/')
#page = fetch_page('https://conradswebsite.com/projects/search-assistant-to-help-find-words-for-the-wordle-game')
#page = fetch_page('https://cnn.com')
print(page)