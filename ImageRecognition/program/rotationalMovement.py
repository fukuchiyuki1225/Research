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

if len(good) > MIN_MATCH_COUNT:
    src_pts = np.float32([kp_q[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dst_pts = np.float32([kp_t[m.trainIdx].pt for m in good]).reshape(-1,1,2)

    # ホモグラフィ行列の推定(M:ホモグラフィ行列，mask:RANSACで使用されたか[0or1])
    M, mask = cv2.findHomography(src_pts,dst_pts,cv2.RANSAC,5.0)
    matchesMask = mask.ravel().tolist()
    print("行列")
    print(M)

    h,w = query.shape[:2] # query画像のサイズを取得
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2) # query画像の四隅の座標を行列に変換
    dst = cv2.perspectiveTransform(pts,M) # Mをquery画像上の座標に変換

    #train画像内で検出された部分を線で囲む
    train = cv2.polylines(train,[np.int32(dst)],True,255,3,cv2.LINE_AA)

    print(dst)
    
else:
    print("Not enough matches are found")
    matchesMask = None

# 特徴点マッチを描画
draw_params = dict(matchColor=(0,255,0),singlePointColor=None,matchesMask=matchesMask,flags=2)
result = cv2.drawMatches(query,kp_q,train,kp_t,good,None,**draw_params)
cv2.imshow("result",result)
cv2.waitKey(0)