import os
import cv2
import numpy as np
from numpy import linalg as LA
import pandas as pd
import math

# 中心座標を求める関数
def centerCoordinates(coordinates):
    value = 0
    for coor in coordinates:
        value += coordinates[coor]
    return value / 4

# なす角を求める関数
def tangent_angle(u: np.ndarray, v: np.ndarray):
    i = np.inner(u, v)
    n = LA.norm(u) * LA.norm(v)
    c = i / n
    return np.rad2deg(np.arccos(np.clip(c, -1.0, 1.0)))

# 物体検出に必要な対応点の数の下限
MIN_MATCH_COUNT = 10

# テンプレート画像の読み込み
template = cv2.imread("./cat.png")

path = "/Users/yuki-f/Documents/SocSEL/Research/Selenium/screenshots/screenshots_cat"
path = "/Users/yuki-f/Documents/SocSEL/Research/Selenium/screenshots/sample"


df = pd.DataFrame(columns=["id", "movement"])

for pathName, dirNames, fileNames in os.walk(path):
    fileLen = len([fileName for fileName in fileNames if not fileName.startswith('.')])
    
    if fileLen == 0:
        continue

    prjId = pathName.rsplit("/")[len(pathName.rsplit("/")) - 1]

    coordinates = []

    for i in range(fileLen):
        fileName = pathName + "/" + prjId + "-" + str(i) + ".png"
        screenshot = cv2.imread(fileName)

        # 検出器生成
        sift = cv2.xfeatures2d.SIFT_create()

        # 画像の特徴量（kp:特徴点の座標情報等, des:特徴量記述子）
        try:
            kp_t,des_t = sift.detectAndCompute(template,None)
            kp_s,des_s = sift.detectAndCompute(screenshot,None)

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

                screenshot = cv2.polylines(screenshot,[np.int32(dst)],True,255,3, cv2.LINE_AA)
                
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
                # print("Not enough matches are found")
                matchesMask = None

            draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                            singlePointColor = None,
                            matchesMask = matchesMask, # draw only inliers
                            flags = 2)
                            
        except Exception as e:
            # print("error")
            continue

        results = cv2.drawMatches(template,kp_t,screenshot,kp_s,good,None,**draw_params)

        # cv2.circle(results, (math.floor(centerOfCoordinates(coordinates[i]["x"])) + 168, math.floor(centerOfCoordinates(coordinates[i]["y"]))), 10, (0, 255, 0), thickness=-1)

        cv2.imshow(fileName, results)
        cv2.waitKey(0)    
    
    # print(prjId) 

    if len(coordinates) <= 0:
        continue

    x1 = centerCoordinates(coordinates[0]["x"])
    x2 = centerCoordinates(coordinates[len(coordinates) - 1]["x"])
    y1 = centerCoordinates(coordinates[0]["y"])
    y2 = centerCoordinates(coordinates[len(coordinates) - 1]["y"])

    print("1: " + str(x1) + ", " + str(y1) + " 2: " + str(x2) + ", " + str(y2))
    print(math.floor(tangent_angle([x1, y1], [x2, y2])))

    angle = math.floor(tangent_angle([x1, y1], [x2, y2]))

    deltaX = math.floor(x2 - x1) if x2 - x1 > 0 else math.ceil(x2 - x1)
    deltaY = math.floor(y2 - y1) if y2 - y1 > 0 else math.ceil(y2 - y1)

    # print(deltaX)
    # print(deltaY)

    if deltaX > 0:
        if deltaY > 0:
            if angle <= 10:
                if abs(deltaX) < abs(deltaY):
                    df = df.append(pd.DataFrame(data=[[prjId, "down"]],columns=["id", "movement"]))
                elif abs(deltaY) < abs(deltaX):
                    df = df.append(pd.DataFrame(data=[[prjId, "right"]],columns=["id", "movement"]))
            else:
                df = df.append(pd.DataFrame(data=[[prjId, "lowerRight"]],columns=["id", "movement"]))
                # print("右下に移動")
        elif deltaY == 0:
            df = df.append(pd.DataFrame(data=[[prjId, "right"]],columns=["id", "movement"]))
            # print("右に移動")
        elif deltaY < 0:
            if angle <= 10:
                if abs(deltaX) < abs(deltaY):
                    df = df.append(pd.DataFrame(data=[[prjId, "up"]],columns=["id", "movement"]))
                elif abs(deltaY) < abs(deltaX):
                    df = df.append(pd.DataFrame(data=[[prjId, "right"]],columns=["id", "movement"]))
            else:
                df = df.append(pd.DataFrame(data=[[prjId, "upperRight"]],columns=["id", "movement"]))
                # print("右上に移動")
    elif deltaX == 0:
        if deltaY == 0:
            o = 0
        elif deltaY > 0:
            df = df.append(pd.DataFrame(data=[[prjId, "down"]],columns=["id", "movement"]))
            # print("下に移動")
        elif deltaY < 0:
            df = df.append(pd.DataFrame(data=[[prjId, "up"]],columns=["id", "movement"]))
            # print("上に移動")
    elif deltaX < 0:
        if deltaY > 0:
            if angle <= 10:
                if abs(deltaX) < abs(deltaY):
                    df = df.append(pd.DataFrame(data=[[prjId, "down"]],columns=["id", "movement"]))
                elif abs(deltaY) < abs(deltaX):
                    df = df.append(pd.DataFrame(data=[[prjId, "left"]],columns=["id", "movement"]))
            else:
                df = df.append(pd.DataFrame(data=[[prjId, "lowerLeft"]],columns=["id", "movement"]))
                # print("左下に移動")
        elif deltaY == 0:
            df = df.append(pd.DataFrame(data=[[prjId, "left"]],columns=["id", "movement"]))
            # print("左に移動")
        elif deltaY < 0:
            if angle <= 10:
                if abs(deltaX) < abs(deltaY):
                    df = df.append(pd.DataFrame(data=[[prjId, "up"]],columns=["id", "movement"]))
                elif abs(deltaY) < abs(deltaX):
                    df = df.append(pd.DataFrame(data=[[prjId, "left"]],columns=["id", "movement"]))
            else:
                df = df.append(pd.DataFrame(data=[[prjId, "upperLeft"]],columns=["id", "movement"]))
                # print("左上に移動")

    # if prjId == "0":
    #     for i in range(len(coordinates)):
    #         print("左上：(" + str(coordinates[i]["x"]["upperLeft"]) + ", " + str(coordinates[i]["y"]["upperLeft"]) + ")")
    #         print("右上：(" + str(coordinates[i]["x"]["upperRight"]) + ", " + str(coordinates[i]["y"]["upperRight"]) + ")")
    #         print("左下：(" + str(coordinates[i]["x"]["lowerLeft"]) + ", " + str(coordinates[i]["y"]["lowerLeft"]) + ")")
    #         print("右下：(" + str(coordinates[i]["x"]["lowerRight"]) + ", " + str(coordinates[i]["y"]["lowerRight"]) + ")")

# df.to_csv("./dataset.csv")

