import os
import pandas as pd
import imageRecognition

# スクリーンショットがあるディレクトリのパス
screenshot = "/mnt/data1/yuki-f/screenshots"

# 検索対象作品で使われているスプライト情報のデータセット
dataset = pd.read_csv("/mnt/data1/yuki-f/dataset.csv", usecols=[2, 4])

# 各スクリーンショットに対して画像認識を行い，オブジェクトの座標位置の時系列データを出力
for pathName1, dirName1, fileNames1 in os.walk(screenshot):
    # 各作品のスクリーンショットの数を取得
    fileLen = len([fileName1 for fileName1 in fileNames1 if not fileName1.startswith(".")])

    # ディレクトリが空（スクショが存在しない）の場合はスキップ
    if fileLen == 0:
        continue

    # 作品idを取得
    prjId = pathName1.rsplit("/")[len(pathName1.rsplit("/")) - 1]

    print(prjId)

    # 取得したオブジェクトの座標位置を時系列データとして格納するdf
    tsData = pd.DataFrame(columns=["time", "sprite", "match", "x", "y"])

    # 作品で使われているデフォルトスプライトのリスト
    sprites = dataset[dataset["p_ID"] == int(prjId)]["sprite-name"].values

    if len(sprites) == 0:
        continue

    spritePath = "/mnt/data1/yuki-f/sprites"

    for sprite in sprites:
        if sprite == "Sprite1":
            sprite = "Cat"

        for pathName2, dirName2, fileNames2 in os.walk(spritePath + "/" + sprite):
            for fileName2 in fileNames2:
                if fileName2.startswith("."):
                    continue

                print("スプライト名: " + sprite)
                print("テンプレート画像のファイル名: " + fileName2)
                
                template = spritePath + "/" + sprite + "/" + fileName2
                
                for j in range(fileLen):
                    screenshot = pathName1 + "/" + prjId + "-" + str(j) + ".png"

                    # print(prjId + " : " + str(j) + " : " + sprite + " : " + fileName2)
                    
                    result = imageRecognition.imageRecognition(template, screenshot)
                    if result is not None:
                        addRow = pd.DataFrame([[j, sprite, result[0], result[1], result[2]]], columns=["time", "sprite", "match", "x", "y"])
                        print(addRow)
                        tsData = tsData.append(addRow)

    if len(tsData) > 0:
        # matchで降順にソート
        tsData = tsData.sort_values("match", ascending=False)
        # time&spriteの重複を削除
        tsData = tsData.drop_duplicates(subset=["time", "sprite"])
        # spriteとtimeで再ソート
        tsData = tsData.sort_values(by=["sprite", "time"])
        tsData.to_csv("/mnt/data1/yuki-f/tsData/" + prjId + ".csv")
    