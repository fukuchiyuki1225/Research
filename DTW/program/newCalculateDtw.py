import os
import pandas as pd
import numpy as np
from tslearn.preprocessing import TimeSeriesScalerMinMax
from tslearn.utils import to_time_series_dataset
import itertools
import time

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
            tsData = pd.read_csv(tsDataPath + "/" + fileName, usecols=["time", "sprite", "x", "y"])

            # 最後にスライスした行番号を保持
            sliceNum = 0

            # 1動作に分割後に出力するtsDataを保持
            outputData = pd.DataFrame(columns=["time", "prjId", "sprite", "x", "y"])

            # tsDataを分割
            for i in range(1, len(tsData)):
                # 分割する条件：スプライトが変わっている or フレームから消える
                if tsData.at[i, "sprite"] != tsData.at[i - 1, "sprite"] or tsData.at[i, "time"] != tsData.at[i - 1, "time"] + 1:
                    for j in range(sliceNum, i):
                        addRow = pd.DataFrame([[tsData.at[j, "time"], prjId, tsData.at[j, "sprite"], round(tsData.at[j, "x"]), round(tsData.at[j, "y"])]], columns=["time", "prjId", "sprite", "x", "y"])
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
                addRow = pd.DataFrame([[tsData.at[i, "time"], prjId, tsData.at[i, "sprite"], round(tsData.at[i, "x"]), round(tsData.at[i, "y"])]], columns=["time", "prjId", "sprite", "x", "y"])
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

# 各1動作の組み合わせごとにDTW距離を算出
def calculateDtw(splittedDataPath):
    # ファイル数の確認
    fileLen = 0
    for pathName, dirName, fileNames in os.walk(splittedDataPath):
        fileLen = len(fileNames)
        for fileName in fileNames:
            if fileName.startswith("."):
                fileLen -= 1
        
    # 1動作のcsvを読み込み，配列に保持（配列のインデックス=動作番号）
    splittedData = []
    prjIds = []
    for i in range(fileLen):
        splittedData.insert(i, pd.read_csv(splittedDataPath + "/" + str(i) + ".csv", usecols=["x", "y"]).values)
        prjIds.insert(i, pd.read_csv(splittedDataPath + "/" + str(i) + ".csv", usecols=["prjId"]).values[0])
            
        # データの正規化(0~1)
        splittedData[i] = TimeSeriesScalerMinMax().fit_transform(to_time_series_dataset([splittedData[i]])).flatten().reshape(-1, 2)
        
    # データ確認用のprint
    # print(splittedData[22])
    # print(prjIds[22])
        
    # 組み合わせを保持
    dataNum = list(range(fileLen))
    combs = list(itertools.combinations(dataNum, 2))
        
    dtwResult = pd.DataFrame(columns=["i", "j", "dtw"])
    count = 0
    start = time.time()
    # 各組み合わせごとにDTW距離を算出
    for comb in combs:
        count += 1
        # 10000の動作ペアごとに実行時間を表示 and dtwResultをcsvファイルに出力
        if count % 10000 == 0:
            elapsed = time.time() - start
            print(str(count) + ": " + str(elapsed))
            start = time.time()
            dtwResult.sort_values("dtw").to_csv("/Users/yuki-f/Documents/SocSEL/Research/DTW/dtw-" + str(count) + ".csv")
            dtwResult = dtwResult[:0]   
        
        i = comb[0]
        j = comb[1]
        
        # 同じ作品に含まれる動作の組み合わせはスキップ
        if prjIds[i] == prjIds[j]:
            continue
        
        dtwVal = dtw(splittedData[i], splittedData[j])[1]
        # print(str(count) + "/" + str(len(combs)) + ": " + str(dtwVal))
        addRow = pd.DataFrame([[i, j, dtwVal]], columns=["i", "j", "dtw"])
        dtwResult = dtwResult.append(addRow)
            
# DTW距離を算出
def dtw(x, y):
    # xのデータ数，yのデータ数をそれぞれTx,Tyに代入
    Tx = len(x)
    Ty = len(y)
    
    # C:各マスの累積コスト，　B：最小コストの行/列番号
    C = np.zeros((Tx, Ty))
    B = np.zeros((Tx, Ty, 2), int)
    
    # 一番初めのマスのコストを，xとyのそれぞれ一番初めの値にする
    C[0, 0] = dist(x[0], y[0])
    
    # 動的計画法を用いる
    # 左下のマスからスタートし，各マスに到達するため最小の累積コストを1マスずつ求める
    
    # 境界条件：両端が左下と右上にあること
    # 単調性：左下から始まり，右，上，右上のいずれかにしか進まないこと
    # 連続性：繋がっていること
    
    # 一番下の行は，真っ直ぐ右にコストが累積される
    for i in range(Tx):
        C[i, 0] = C[i - 1, 0] + dist(x[i], y[0])
        B[i, 0] = [i - 1, 0]
        
    # 同様に一番左の列は，真っ直ぐ上にコストが累積される
    for j in range(1, Ty):
        C[0, j] = C[0, j - 1] + dist(x[0], y[j])
        B[0, j] = [0, j - 1]
        
    # その他のマスの累積コストを求める
    for i in range(1, Tx):
        for j in range(1, Ty):
            pi, pj, m = get_min(C[i - 1, j],
                                C[i, j - 1],
                                C[i - 1, j - 1],
                                i, j)
            # get_minで返ってきた最小コストを累積コストに足す
            C[i, j] = dist(x[i], y[j]) + m
            # get_minで返ってきた最小コストの行/列番号を保持
            B[i, j] = [pi, pj]
    # 最終的な右上（最終の到達点）のコスト
    cost = C[-1, -1]
    
    path = [[Tx - 1, Ty - 1]]
    
    # 逆順にたどることでパスを求める
    i = Tx - 1
    j = Ty - 1
    
    while((B[i, j][0] != 0) or (B[i, j][1] != 0)):
        path.append(B[i, j])
        i, j = B[i, j].astype(int)
    path.append([0, 0])
    return np.array(path), cost, C

# 距離算出
def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

# 最小値算出
def get_min(m0, m1, m2, i, j):
    if m0 < m1:
        if m0 < m2:
            return i - 1, j, m0
        else:
            return i - 1, j - 1, m2
    else:
        if m1 < m2:
            return i, j - 1, m1
        else:
            return i - 1, j - 1, m2

        
# splitTsData("/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/dataset/tsData5", "/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/dataset/splitted5")

calculateDtw("/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/dataset/splitted5")