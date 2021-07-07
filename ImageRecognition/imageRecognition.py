import cv2
import numpy as np
import traceback
import math

# 中心座標を求める関数
def centerCoordinate(coordinates):
    value = 0
    for coor in coordinates:
        value += coordinates[coor]
    return value / 4

# 画像認識を行い，オブジェクトの座標位置(中心座標)を返す関数
def imageRecognition(template, screenshot):
    template = cv2.imread(template)
    screenshot = cv2.imread(screenshot)

    # 物体検出に必要な対応点の数の下限
    MIN_MATCH_COUNT = 10

    # オブジェクトの座標位置を格納するリスト
    coordinates = []

    # 検出器生成
    sift = cv2.xfeatures2d.SIFT_create()

    try:
        # 画像の特徴量（kp:特徴点の座標情報等, des:特徴量記述子）
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
        if len(good) >= MIN_MATCH_COUNT:
            src_pts = np.float32([ kp_t[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp_s[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)

            h,w = template.shape[:2]
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)

            if (M is None):
                # print("not match")
                return None

            dst = cv2.perspectiveTransform(pts,M)
                
            flattenCoors = np.int32(dst).flatten()

            # 検出した物体の四隅の座標
            coordinates.append(
                {
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

            # print("match")
            
            """
            座標確認用
            cv2.circle(screenshot, (coordinates[0]["x"]["upperLeft"], coordinates[0]["y"]["upperLeft"]), 10, (225, 0, 0), thickness=-1)
            cv2.circle(screenshot, (coordinates[0]["x"]["lowerLeft"], coordinates[0]["y"]["lowerLeft"]), 10, (225, 0, 0), thickness=-1)
            cv2.circle(screenshot, (coordinates[0]["x"]["lowerRight"], coordinates[0]["y"]["lowerRight"]), 10, (225, 0, 0), thickness=-1)
            cv2.circle(screenshot, (coordinates[0]["x"]["upperRight"], coordinates[0]["y"]["upperRight"]), 10, (225, 0, 0), thickness=-1)

            print("upperLeft X: " + str(coordinates[0]["x"]["upperLeft"]) + " Y: " + str(coordinates[0]["y"]["upperLeft"]))
            print("lowerLeft X: " + str(coordinates[0]["x"]["lowerLeft"]) + " Y: " + str(coordinates[0]["y"]["lowerLeft"]))
            print("lowerRight X: " + str(coordinates[0]["x"]["lowerRight"]) + " Y: " + str(coordinates[0]["y"]["lowerRight"]))
            print("upperRight X: " + str(coordinates[0]["x"]["upperRight"]) + " Y: " + str(coordinates[0]["y"]["upperRight"]))

            cv2.imshow("", screenshot)
            cv2.waitKey(0)
            """

            return [len(good), centerCoordinate(coordinates[0]["x"]), centerCoordinate(coordinates[0]["y"])]

        else:
            # print("not match")
            return None          

    except Exception as e:
        print(traceback.format_exc())

    

