import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tslearn.clustering import TimeSeriesKMeans
from tslearn.utils import to_time_series_dataset
from tslearn.preprocessing import TimeSeriesScalerMinMax

def splitTsData(path):
    # 多次元連想配列に切り分けたデータを保持
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

            # csvからデータを分ける
            for i in range(1, len(data)):
                # 1.スプライトが変わっている
                if data.at[i, "sprite"] != data.at[i-1, "sprite"]:
                    for j in range(sliceNum, i):
                        addRow = pd.DataFrame([[prjId + "_" + data.at[i-1, "sprite"] + "_" + str(sprNum), data.at[j, "time"], data.at[j, "x"], data.at[j, "y"]]], columns=["prjId_sprite_sprNum", "time", "x", "y"])
                        tsData = tsData.append(addRow)
                    sliceNum = i
                    sprNum = 0
            
                # 2.フレームから一旦消え，別のフレームでまた復活している
                elif data.at[i, "time"] != data.at[i-1, "time"] + 1:
                    for j in range(sliceNum, i):
                        addRow = pd.DataFrame([[prjId + "_" + data.at[i-1, "sprite"] + "_" + str(sprNum), data.at[j, "time"], data.at[j, "x"], data.at[j, "y"]]], columns=["prjId_sprite_sprNum", "time", "x", "y"])
                        tsData = tsData.append(addRow)
                    sliceNum = i
                    sprNum += 1
                    
            for i in range(sliceNum, len(data)):
                addRow = pd.DataFrame([[prjId + "_" + data.at[len(data)-1, "sprite"] + "_" + str(sprNum), data.at[i, "time"], data.at[i, "x"], data.at[i, "y"]]], columns=["prjId_sprite_sprNum", "time", "x", "y"])
                tsData = tsData.append(addRow)

    return tsData

# 時系列データをクラスタリング
def clusteringTsData(tsData, nc):
    coors = []
    for num in tsData["prjId_sprite_sprNum"].unique():
        addCoor = np.array(tsData[tsData["prjId_sprite_sprNum"]==num][["x","y"]])
        if len(addCoor) <= 1:
            continue
        coors.append(addCoor)
        
    coors = TimeSeriesScalerMinMax().fit_transform(to_time_series_dataset(coors))

    print(coors)

    dba_km = TimeSeriesKMeans(n_clusters=nc,
                            n_init=5,
                            metric="dtw",
                            verbose=False,
                            max_iter_barycenter=100,
                            random_state=22)

    pred = dba_km.fit_predict(coors)

    cr = []

    for i in range(nc):
        cr.append([])
        
    for num,c in zip(tsData["prjId_sprite_sprNum"].unique(),pred):
        cr[c].append(np.array(tsData[tsData["prjId_sprite_sprNum"]==num][["prjId_sprite_sprNum","time","x","y"]]))
        
    for i in range(len(cr)):
        for j in range(2):
            plt.figure()
            for r in cr[i]:
                t = np.array([])
                v = np.array([])
                vType = ""
                for d in r:
                    t = np.append(t, d[1])
                    v = np.append(v, d[j + 2])
                if j == 0:
                    vType = "x"
                    plt.title("cluster" + str(i) + ": " + vType)
                    plt.ylabel(vType)
                    plt.ylim(0, 490)
                else:
                    vType = "y"
                    plt.title("cluster" + str(i) + ": " + vType)
                    plt.ylabel(vType)
                    plt.ylim(0, 370)
                plt.xlabel("time")
                plt.plot(t, v)
                plt.savefig("nc" + str(nc) + "_cluster" + str(i) + "_" + vType)
            print("cluster" + str(i) + " : " + vType + " done")

dataset = "/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/tsData"
clusteringTsData(splitTsData(dataset), 15)
