import os
import pandas as pd

# 各作品の時系列データを１つの動作ごとに分割
def splitTsData(tsDataPath, savePath):
    for pathName, dirName, fileNames in os.walk(tsDataPath):
        # 動作番号
        mvNum = 0
        for fileName in fileNames:
            if fileName.startswith("."):
                continue

            prjId = fileName.rsplit(".")[0]

            # 分割前のtsData
            tsData = pd.read_csv(tsDataPath + "/" + fileName, usecols=[1, 2, 4, 5])

            # 最後にスライスした行番号を保持
            sliceNum = 0

            # 1動作に分割後に出力するtsDataを保持
            outputData = pd.DataFrame(columns=["time", "prjId", "sprite", "x", "y"])

            # tsDataを分割
            for i in range(1, len(tsData)):
                # 分割する条件：スプライトが変わっている or フレームから消える
                if tsData.at[i, "sprite"] != tsData.at[i - 1, "sprite"] or tsData.at[i, "time"] != tsData.at[i - 1, "time"] + 1:
                    for j in range(sliceNum, i):
                        addRow = pd.DataFrame([[tsData.at[j, "time"], prjId, tsData.at[j, "sprite"], tsData.at[j, "x"], tsData.at[j, "y"]]], columns=["time", "prjId", "sprite", "x", "y"])
                        outputData = outputData.append(addRow)
                    sliceNum = i
                    outputData = outputData.reset_index(drop=True)
                    
                    if checkData(outputData):
                        outputData = outputData[:0]
                        continue

                    outputData.to_csv(savePath + "/" + str(mvNum) + ".csv")
                    outputData = outputData[:0]
                    mvNum += 1

            for i in range(sliceNum, len(tsData)):
                addRow = pd.DataFrame([[tsData.at[i, "time"], prjId, tsData.at[i, "sprite"], tsData.at[i, "x"], tsData.at[i, "y"]]], columns=["time", "prjId", "sprite", "x", "y"])
                outputData = outputData.append(addRow)
            outputData = outputData.reset_index(drop=True)
            
            # 1動作の全てのフレームにおいて座標が同じでないかを判定
            if checkData(outputData):
                continue

            outputData.to_csv(savePath + "/" + str(mvNum) + ".csv")

# 1動作の座標データが条件を満たすかを判定
# 返り値がTrueの場合，その1動作は除外
def checkData(outputData):
    # 条件：1動作のフレーム数が5以上
    if len(outputData) < 5:
        return True

    # 条件：値が負でない
    for i in range(len(outputData)):
        if outputData.at[i, "x"] < 0 or outputData.at[i, "y"] < 0:
            return True

    # 条件：1動作の全てのフレームにおいて座標が同じでない
    firstX = outputData.at[0, "x"]
    firstY = outputData.at[0, "y"]
    for i in range(1, len(outputData)):
        if outputData.at[i, "x"] != firstX or outputData.at[i, "y"] != firstY:
            return False
    return True

splitTsData("/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/dataset/tsData5", "/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/dataset/splitted5")