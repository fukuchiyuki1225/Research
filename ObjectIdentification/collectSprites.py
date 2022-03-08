from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
import time

driver = webdriver.Chrome("/usr/local/bin/chromedriver")
driver.get("https://scratch.mit.edu/projects/editor/")

wait = WebDriverWait(driver, 15)
loadClassName = "action-menu_main-icon_1ktMc"

try:
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, loadClassName)))
except TimeoutException as te:
    print("timeout")

for i in range(330, 339):
    addSprite = driver.find_element_by_class_name("action-menu_main-icon_1ktMc")
    addSprite.click()

    sprites = driver.find_elements_by_class_name("library-item_library-item_1DcMO")[i]
    sprites.click()

for i in range(11):
    menu = driver.find_elements_by_class_name("sprite-selector_sprite_21WnR")[i]
    menu.click()
    ActionChains(driver).context_click(menu).perform()

    output = driver.find_elements_by_class_name("context-menu_menu-item_3cioN")[i + 1 + i * 2]
    output.click()

time.sleep(3)
driver.close()

