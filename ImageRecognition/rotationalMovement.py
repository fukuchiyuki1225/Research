import numpy as np
import matplotlib.pyplot as plt
import cv2

# 画像の読み込み
query = cv2.imread("./cat.png") #検出したい画像
train = cv2.imread("./sample1.png") #検出対象の画像

# 検出器生成
sift = cv2.xfeatures2d.SIFT_create()

# 画像の特徴量（kp:特徴点の座標情報等，des:特徴量記述子）
kp_q, des_q = sift.detectAndCompute(query,None)
kp_t, des_t = sift.detectAndCompute(train,None)

# k-近傍探索の準備
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE,tress=5)
search_params = dict(checks = 50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

# k-近傍探索を用いて特徴点のマッチング
matches = flann.knnMatch(des_q,des_t,k=2)

# Loweの比率検定に従って、ベストマッチした特徴量を配列goodに保持
good = []
for m,n in matches:
    if m.distance < 0.7*n.distance:
        good.append(m)

# 物体検出に必要な対応点の数の下限
MIN_MATCH_COUNT = 10
