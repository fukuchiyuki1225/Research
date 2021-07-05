import os
import pandas as pd
import imageRecognition
import cv2

templete = ""

# スクリーンショットがあるディレクトリのパス
screenshot = "/Users/yuki-f/Documents/SocSEL/Research/Selenium/dataset/sample/screenshots"

# 各スクリーンショットに対して画像認識を行い，オブジェクトの座標位置の時系列データを出力
for pathName, dirName, fileNames in os.walk(screenshot):
    # 各作品のスクリーンショットの数を取得
    fileLen = len([fileName for fileName in fileNames if not fileName.startswith(".")])

    # ディレクトリが空（スクショが存在しない）の場合はスキップ
    if fileLen == 0:
        continue

    prjId = pathName.rsplit("/")[len(pathName.rsplit("/")) - 1]

    tsData = pd.DataFrame(columns=["time", "sprite", "x", "y"])

    for i in range(fileLen):
        fileName = pathName + "/" + prjId + "-" + str(i) + ".png"

        print(imageRecognition.imageRecognition(cv2.imread(templete), cv2.imread(fileName)))
        
        

    