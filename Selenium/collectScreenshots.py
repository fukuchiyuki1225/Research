import os
import time
import pandas as pd
# import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

ids = pd.read_csv("/Users/socsel/dataset.csv", usecols=["p_ID"], dtype="str")

for id in ids["p_ID"]:
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.get("https://scratch.mit.edu/projects/" + id)

    wait = WebDriverWait(driver, 15)
    loadClassName = "loader_bottom-block_1-3rO"

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, loadClassName)))
        wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, loadClassName)))
    except TimeoutException as te:
        print("timeout")
        continue

    savePath = "/Users/socsel/screenshots/" + id
    if not os.path.isdir(savePath):
        os.mkdir(savePath)

    start = driver.find_element_by_class_name("stage_green-flag-overlay_gNXnv")
    start.click()

    time.sleep(0.03)

    start = time.time()
    for i in range(100):
        time.sleep(0.2)
        end = driver.find_elements_by_css_selector(".green-flag_green-flag_1kiAo.green-flag_is-active_2oExT")
        if len(end) == 0:
            break
        png = driver.find_element_by_class_name("stage-wrapper_stage-canvas-wrapper_3ewmd").screenshot_as_png
        try:
            with open(savePath + "/" + id + "-" + str(i) + ".png", "wb") as f:
                f.write(png)
        except OSError as oe:
            print("save error")
    elapsed_time = time.time() - start
    print(elapsed_time)

    driver.close()

