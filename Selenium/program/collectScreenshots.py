import os
import time
import pandas as pd
# import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ids = pd.read_csv("/Users/socsel/dataset.csv", usecols=["p_ID"], dtype="str")
# retryIds = pd.read_csv("/Users/socsel/retryIds.csv", usecols=["p_ID"], dtype="str")
retryIds = pd.read_csv("/Users/yuki-f/Desktop/retryIds.csv", usecols=["p_ID"], dtype="str")
retryIds = list(retryIds)

# for id in ids["p_ID"]:
for id in range(276713154, 287868002):
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.get("https://scratch.mit.edu/projects/" + str(id))

    wait = WebDriverWait(driver, 15)
    loadClassName = "loader_bottom-block_1-3rO"

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, loadClassName))) # 作品のロード開始を待機
        wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, loadClassName))) # 作品のロード完了を待機
    except TimeoutException as te:
        print(str(id) + ": timeout") # 作品が存在していないため，スキップ
        driver.close()
        continue

    try:
        start = driver.find_element_by_class_name("stage_green-flag-overlay_gNXnv")
        start.click()
    except Exception as e:
        print(str(id) + ": crash error") # Scratchがクラッシュするエラー
        retryIds.append(str(id)) # エラーが発生した場合，後ほど再試行するためidを配列に追加して保持
        driver.close()
        continue

    savePath = "/Users/yuki-f/Desktop/screenshots/" + str(id)
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
            print(str(id) + ": error") # 予期せぬエラー
            retryIds.append(str(id)) # エラーが発生した場合，後ほど再試行するためidを配列に追加して保持
            driver.close()
            break

        try:
            with open(savePath + "/" + str(id) + "-" + str(i) + ".png", "wb") as f:
                f.write(png)
            print("save png: " + str(i))
        except OSError as oe:
            print("save error") # 画像保存失敗エラー
            driver.close()
            continue

    elapsedTime = time.time() - startTime
    print(str(id) + ": " + str(elapsedTime) + "s")

    df = pd.DataFrame(retryIds, columns=["p_ID"])

    if len(retryIds) > 1:
        df.to_csv("retryIds.csv")

    driver.close()

driver.quit()

