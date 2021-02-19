import cv2
import pandas as pd
import os

savePath = "./results/"
project = "129889092"

# データ保存用のディレクトリ作成
if not os.path.isdir(savePath + project):
    os.mkdir(savePath + project)
    os.mkdir(savePath + project + "/csv")
    os.mkdir(savePath + project + "/img")

# テンプレート画像
template = cv2.imread("./cat.png",0)

# 検出器生成
sift = cv2.xfeatures2d.SIFT_create()
bf = cv2.BFMatcher()

# テンプレート画像の特徴量検出（kp:特徴点の座標情報等, des:特徴量記述子）
kp_t,des_t = sift.detectAndCompute(template,None)

for i in range(20):
    ssName = project + "-" + str(i)

    # 対象画像
    screenshot = cv2.imread("./screenshots/" + project + "/" + ssName + ".png",0)

    # 対象画像の特徴量検出
    kp_s,des_s = sift.detectAndCompute(screenshot,None)

    # 特徴点のマッチング
    matches = bf.match(des_t,des_s)

    # マッチング精度の高いものを降順でソート
    matches = sorted(matches,key=lambda x:x.distance)

    # dataFrame作成
    df = pd.DataFrame(columns=["x_screenshot","y_screenshot","x_template","y_template","Distance"])

    # dfに各情報を格納
    for l in range(len(matches)):
        df.loc["Matches"+str(l)] = [kp_s[matches[l].trainIdx].pt[0],kp_s[matches[l].trainIdx].pt[1],kp_t[matches[l].queryIdx].pt[0],kp_t[matches[l].queryIdx].pt[1],matches[l].distance]

    # csvへ変換＆保存
    df.to_csv(savePath + project + "/csv/" + ssName + ".csv")

    # マッチングした特徴点上位10件を示し，画像を保存
    img_match = cv2.drawMatches(template, kp_t, screenshot, kp_s, matches[:10], None, flags=2)
    cv2.imwrite(savePath + project + "/img/" + ssName + ".png",img_match)

    # 座標確認用
    # img_zahyou1 = cv2.circle(screenshot,(331,156),10,(0,0,255),0)
    # img_zahyou2 = cv2.circle(template,(39,123),10,(0,0,255),0)

    # cv2.imshow("", img_zahyou1)
    # cv2.waitKey(0)

    # cv2.imshow("", img_zahyou2)
    # cv2.waitKey(0)
