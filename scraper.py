from selenium import webdriver

# Specify the path to the Chrome binary you want to use
chrome_binary_path = "/Users/furkansuren/Desktop/chrome-mac-arm64/Google Chrome for Testing"  # Replace with the actual path

# Set up Chrome options to use the specified binary
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = chrome_binary_path

# Create a WebDriver instance with the custom Chrome binary
driver = webdriver.Chrome()

driver.get("sahibinden.com")


