from selenium import webdriver

driver = webdriver.Chrome("/usr/local/bin/chromedriver")
driver.get("https://google.co.jp")

text = driver.find_element_by_name("q")
text.send_keys("selenium")
text.submit()