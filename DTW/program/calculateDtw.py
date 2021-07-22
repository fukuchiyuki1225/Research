import os
import numpy as np
import pandas as pd
from tslearn.preprocessing import TimeSeriesScalerMinMax
from tslearn.utils import to_time_series_dataset
import matplotlib.pyplot as plt
import seaborn as sns

# 各作品の時系列データを１つの動作ごとに分割する
def splitTsData(path):
    tsData = pd.DataFrame(columns=["prjId_sprite_sprNum", "time", "x", "y"])
    for pathName, dirName, fileNames in os.walk(path):
        for fileName in fileNames:
            if fileName.startswith("."):
                continue
                
            prjId = fileName.rsplit(".")[0]
            
            data = pd.read_csv(path + "/" + fileName, usecols=[0, 1, 2, 4, 5])
                    
            # 最後にスライスしたインデックスを保持
            sliceNum = 0

            # 同じスプライトで何個目の動きかを保持
            sprNum = 0

            mvNum = 0

            # csvからデータを分ける
            for i in range(1, len(data)):
                # 1.スプライトが変わっている
                if data.at[i, "sprite"] != data.at[i-1, "sprite"]:
                    for j in range(sliceNum, i):
                        addRow = pd.DataFrame([[prjId + "_" + data.at[i-1, "sprite"] + "_" + str(sprNum), data.at[j, "time"], data.at[j, "x"], data.at[j, "y"]]], columns=["prjId_sprite_sprNum", "time", "x", "y"])
                        tsData = tsData.append(addRow)
                    sliceNum = i
                    sprNum = 0
                    mvNum += 1
            
                # 2.フレームから一旦消え，別のフレームでまた復活している
                elif data.at[i, "time"] != data.at[i-1, "time"] + 1:
                    for j in range(sliceNum, i):
                        addRow = pd.DataFrame([[prjId + "_" + data.at[i-1, "sprite"] + "_" + str(sprNum), data.at[j, "time"], data.at[j, "x"], data.at[j, "y"]]], columns=["prjId_sprite_sprNum", "time", "x", "y"])
                        tsData = tsData.append(addRow)
                    sliceNum = i
                    sprNum += 1
                    mvNum += 1
                    
            for i in range(sliceNum, len(data)):
                addRow = pd.DataFrame([[prjId + "_" + data.at[len(data)-1, "sprite"] + "_" + str(sprNum), data.at[i, "time"], data.at[i, "x"], data.at[i, "y"]]], columns=["prjId_sprite_sprNum", "time", "x", "y"])
                tsData = tsData.append(addRow)
    tsData.to_csv("tsData.csv")
    return tsData

# 距離計算
def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

# 最小値を求める
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

# DTW距離を求める関数
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

# DTW距離を計算し，ヒートマップを描画
def drawHeatmap(tsData):
    print("drawHeatmap")
    lastData = tsData

    coors = []
    for num in tsData["prjId_sprite_sprNum"].unique():
        addCoor = np.array(tsData[tsData["prjId_sprite_sprNum"]==num][["x","y"]])
        if len(addCoor) < 5:
            lastData = lastData[lastData["prjId_sprite_sprNum"]!=num]
            continue
        coors.append(addCoor)

    coors = TimeSeriesScalerMinMax().fit_transform(to_time_series_dataset(coors))

    heatmapData = np.array([])
    dtwResult = pd.DataFrame(columns=["i","j","dtw"])
    for i in range(len(coors)):
        coors1 = coors[i]    
        for m in range(len(coors1)):
            if np.isnan(coors1[m][0]) or np.isnan(coors1[m][1]):
                coors1 = np.delete(coors1, np.s_[m:], 0)
                break
        for j in range(len(coors)):
            coors2 = coors[j]
            for n in range(len(coors2)):
                if np.isnan(coors2[n][0]) or np.isnan(coors2[n][1]):
                    coors2 = np.delete(coors2, np.s_[n:], 0)
                    break
            addResult = pd.DataFrame([[i, j, dtw(coors1, coors2)[1]]], columns=["i","j","dtw"])
            heatmapData = np.append(heatmapData, dtw(coors1, coors2)[1])
            dtwResult = dtwResult.append(addResult)

    dtwResult = dtwResult.sort_values("dtw")
    dtwResult.to_csv("dtw.csv")
    lastData.to_csv("lastData.csv")

    heatmapData = heatmapData.reshape(len(coors), -1)
    plt.figure()
    sns.heatmap(heatmapData, cmap='Blues')
    plt.savefig("heatmap.png")

def checkData(lastData, n1, n2):
    count = 0
    for num in lastData["prjId_sprite_sprNum"].unique():
        if count == n1 or count == n2:
            print(lastData[lastData["prjId_sprite_sprNum"]==num])
        count += 1

tsData = splitTsData("/Users/yuki-f/Desktop/tsData6")
drawHeatmap(tsData)



        