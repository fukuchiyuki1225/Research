import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 二乗距離を計算する関数
def dist(x, y):
    return (x - y)**2

# 一番小さい値と，その値のインデックスを返す
# m0:左のコスト， m1:下のコスト, m2:左下のコスト, i:行番号, j:列番号
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


x1 = pd.read_csv("/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/tsData/99107851.csv", usecols=[4], encoding="shift-jis").values
x2 = pd.read_csv("/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/tsData2/99164552.csv", usecols=[4], encoding="shift-jis").values

print(x1)

x1 = x1[0:15]
x2 = x2[43:49]

path, dtw_dist, C = dtw(x1, x2)

for line in path:
    plt.plot(line, [x1[line[0]], x2[line[1]]], linewidth=0.8, c="gray")
plt.plot(x1)
plt.plot(x2)
plt.show()

y1 = pd.read_csv("/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/tsData/99107851.csv", usecols=[5], encoding="shift-jis").values
y2 = pd.read_csv("/Users/yuki-f/Documents/SocSEL/Research/ImageRecognition/tsData2/99164552.csv", usecols=[5], encoding="shift-jis").values

y1 = y1[0:15]
y2 = y2[43:49]

path, dtw_dist, C = dtw(y1, y2)

for line in path:
    plt.plot(line, [y1[line[0]], y2[line[1]]], linewidth=0.8, c="gray")
plt.plot(y1)
plt.plot(y2)
plt.show()


