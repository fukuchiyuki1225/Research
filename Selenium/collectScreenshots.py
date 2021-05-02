import os
import time
import pandas as pd
# import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

ids = pd.read_csv("/Users/yuki-f/Documents/SocSEL/Research/Selenium/sample.csv", usecols=["p_ID"], dtype="str")
retryIds = []

for id in ids["p_ID"]:
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.get("https://scratch.mit.edu/projects/" + id)

    wait = WebDriverWait(driver, 15)
    loadClassName = "loader_bottom-block_1-3rO"

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, loadClassName))) # 作品のロード開始を待機
        wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, loadClassName))) # 作品のロード完了を待機
    except TimeoutException as te:
        print(id + ": timeout") # 作品が存在していないため，スキップ
        continue

    try:
        start = driver.find_element_by_class_name("stage_green-flag-overlay_gNXnv")
        start.click()
    except Exception as e:
        print(id + ": crash error") # Scratchがクラッシュするエラー
        retryIds.append(id) # エラーが発生した場合，後ほど再試行するためidを配列に追加して保持
        continue

    savePath = "/Users/yuki-f/Documents/SocSEL/Research/Selenium/screenshots/" + id
    if not os.path.isdir(savePath):
        os.mkdir(savePath)
    
    startTime = time.time()

    for i in range(100):
        time.sleep(0.2)

        try:
            end = driver.find_elements_by_css_selector(".green-flag_green-flag_1kiAo.green-flag_is-active_2oExT")
            if len(end) == 0:
                break # 作品のプログラムが終了していれば，スクリーンショット収集終了
            png = driver.find_element_by_class_name("stage-wrapper_stage-canvas-wrapper_3ewmd").screenshot_as_png # スクリーンショットを取得
        except Exception as e:
            print(id + ": " + e) # 予期せぬエラー
            retryIds.append(id) # エラーが発生した場合，後ほど再試行するためidを配列に追加して保持
            break

        try:
            with open(savePath + "/" + id + "-" + str(i) + ".png", "wb") as f:
                f.write(png)
            print("save png: " + str(i))
        except OSError as oe:
            print("save error") # 画像保存失敗エラー
            continue

    elapsedTime = time.time() - startTime
    print(id + ": " + str(elapsedTime) + "s")

    df = pd.DataFrame(retryIds, columns=["p_ID"])

    if len(retryIds) > 1:
        df.to_csv("retryIds.csv")

    driver.close()

driver.quit()

