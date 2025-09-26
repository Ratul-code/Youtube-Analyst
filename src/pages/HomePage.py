from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class HomePage:
    def __init__(self, driver,URL):
        self.driver = driver
        self.URL = URL
    def load(self):
        self.driver.get(self.URL)
        assert "YouTube" in self.driver.title
    def get_search_suggestion (self, query,depth = 5):
        search_input = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_input.clear()
        search_input.send_keys(query)
        search_list = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='listbox']"))
        )
        options = search_list.find_elements(By.CSS_SELECTOR, "[role='option']")[:depth]
        return [option.text for option in options]