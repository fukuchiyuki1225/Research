import os
import cv2
import numpy as np
import pandas as pd
import math

# 中心座標を求める関数
def centerOfCoordinates(coordinates):
    value = 0
    for coor in coordinates:
        value += coordinates[coor]
    return value / 4

input = []
input.append(cv2.imread("./input.png"))
input.append(cv2.imread("./input2.png"))

template = cv2.imread("./cat.png")

# 物体検出に必要な対応点の数の下限
MIN_MATCH_COUNT = 10

coordinates = []

# 検出器生成
sift = cv2.xfeatures2d.SIFT_create()

for i in range(len(input)):
    # 画像の特徴量（kp:特徴点の座標情報等, des:特徴量記述子）
    kp_t,des_t = sift.detectAndCompute(template,None)
    kp_s,des_s = sift.detectAndCompute(input[i],None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE,tress=5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des_t,des_s,k=2)

    good = []
    for m,n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    # 対応点がMIN_MATCH_COUNT以上あれば物体を検出
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([ kp_t[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp_s[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        matchesMask = mask.ravel().tolist()

        h,w = template.shape[:2]
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)

        input[i] = cv2.polylines(input[i],[np.int32(dst)],True,255,3, cv2.LINE_AA)
            
        flattenCoors = np.int32(dst).flatten()

        coordinates.append(
            {
                "index": i,
                "x": {
                    "upperLeft": flattenCoors[0], 
                    "lowerLeft": flattenCoors[2],
                    "lowerRight": flattenCoors[4],
                    "upperRight": flattenCoors[6]
                },
                "y": {
                    "upperLeft": flattenCoors[1], 
                    "lowerLeft": flattenCoors[3],
                    "lowerRight": flattenCoors[5],
                    "upperRight": flattenCoors[7]
                }
            }
        )

    else:
        print("Not enough matches are found")
        matchesMask = None

    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                    singlePointColor = None,
                    matchesMask = matchesMask, # draw only inliers
                    flags = 2)

    results = cv2.drawMatches(template,kp_t,input[i],kp_s,good,None,**draw_params)

    # cv2.circle(results, (math.floor(centerOfCoordinates(coordinates[i]["x"])) + 168, math.floor(centerOfCoordinates(coordinates[i]["y"]))), 10, (0, 255, 0), thickness=-1)

    cv2.imshow("result", results)
    cv2.waitKey(0)

x1 = centerOfCoordinates(coordinates[0]["x"])
x2 = centerOfCoordinates(coordinates[len(coordinates) - 1]["x"])
y1 = centerOfCoordinates(coordinates[0]["y"])
y2 = centerOfCoordinates(coordinates[len(coordinates) - 1]["y"])

deltaX = math.floor(x2 - x1) if x2 - x1 > 0 else math.ceil(x2 - x1)
deltaY = math.floor(y2 - y1) if y2 - y1 > 0 else math.ceil(y2 - y1)

movement = ""

if deltaX > 0:
    if deltaY > 0:
        movement = "lowerRight"
        print("右下に移動")
    elif deltaY == 0:
        movement = "right"
        print("右に移動")
    elif deltaY < 0:
        movement = "upperRight"
        print("右上に移動")
elif deltaX == 0:
    if deltaY > 0:
        movement = down
        print("下に移動")
    elif deltaY < 0:
        movement = up
        print("上に移動")
elif deltaX < 0:
    if deltaY > 0:
        movement = "lowerLeft"
        print("左下に移動")
    elif deltaY == 0:
        movement = "left"
        print("左に移動")
    elif deltaY < 0:
        movement = "upperLeft"
        print("左上に移動")  

df = pd.read_csv("dataset.csv")
print(df.query("movement == @movement")["id"])