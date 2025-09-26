from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service

def setup_driver():
    """Initialize and return a configured webdriver."""
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Optional: run in headless mode
    # service = Service(ChromeDriverManager().install())
    # return webdriver.Chrome(service=service, options=options)

    return webdriver.Chrome()

