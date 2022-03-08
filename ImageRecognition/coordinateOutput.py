import os
import pandas as pd
import cv2
import imageRecognition
from concurrent.futures import ProcessPoolExecutor


# 各スクリーンショットに対して画像認識を行い，オブジェクトの座標位置の時系列データを出力
def work(prjId):
    if os.path.exists(f"/mnt/data1/yuki-f/tsData/{prjId}.csv") or os.path.exists(f"/mnt/data1/yuki-f/tsData_null/{prjId}.csv"):
        return f"[{prjId}] skip"

    screenshots_path = "/mnt/data1/yuki-f/screenshots"
    dataset = pd.read_csv("/mnt/data1/yuki-f/dataset.csv", usecols=[2, 4])

    pathName1 = os.path.join(screenshots_path, prjId)
    fileNames1 = os.listdir(pathName1)

    # 各作品のスクリーンショットの数を取得
    fileLen = len([fileName1 for fileName1 in fileNames1 if not fileName1.startswith(".")])

    # ディレクトリが空（スクショが存在しない）の場合はスキップ
    if fileLen == 0:
        return

    # 作品で使われているデフォルトスプライトのリスト
    sprites = dataset[dataset["p_ID"] == int(prjId)]["sprite-name"].values

    if len(sprites) == 0:
        return

    print(f"[{prjId}] START")


    spritePath = "/mnt/data1/yuki-f/sprites"

    template_paths = []
    for sprite in sprites:
        if sprite == "Sprite1":
            sprite = "Cat"
        
        template_paths.extend([os.path.join(spritePath, sprite, sprite_file) for sprite_file in os.listdir(os.path.join(spritePath, sprite)) if not sprite_file.startswith(".")])

    sift = cv2.SIFT_create()

    templates = []
    for template_path in template_paths:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"[{prjId}] {template_path} is empty")
            continue
        kp_t, des_t = sift.detectAndCompute(template, None)
        if des_t is not None:
            templates.append((template_path, (template, kp_t, des_t)))
        else:
            print(f"[{prjId}] can't SIFT {template_path}")
    
    
    screenshots = []
    for i in range(fileLen):
        screenshot = cv2.imread(os.path.join(pathName1, f"{prjId}-{str(i)}.png"), cv2.IMREAD_GRAYSCALE)
        if screenshot is None:
            print(f"[{prjId}] {prjId}-{str(i)}.png is empty")
            continue        

        kp_s, des_s = sift.detectAndCompute(screenshot, None)
        if des_s is not None:
            screenshots.append((i, (screenshot, kp_s, des_s)))
        else:
            print(f"[{prjId}] can't SIFT {prjId}-{str(i)}.png")


    # 取得したオブジェクトの座標位置を時系列データとして格納するdf
    tsData = pd.DataFrame(columns=["time", "sprite", "match", "x", "y"])
    for template_path, template in templates:
        print(f"[{prjId}] テンプレート画像のファイル名: {template_path}")
        for i, screenshot in screenshots:
            result = imageRecognition.imageRecognition(template, screenshot)
            if result is not None:
                addRow = pd.DataFrame([[i, template_path.split("/")[-2], result[0], result[1], result[2]]], columns=["time", "sprite", "match", "x", "y"])
                tsData = tsData.append(addRow)


    if len(tsData) > 0:
        # matchで降順にソート
        tsData = tsData.sort_values("match", ascending=False)
        # time&spriteの重複を削除
        tsData = tsData.drop_duplicates(subset=["time", "sprite"])
        # spriteとtimeで再ソート
        tsData = tsData.sort_values(by=["sprite", "time"])
        tsData.to_csv("/mnt/data1/yuki-f/tsData/" + prjId + ".csv")
    
        return f"[{prjId}] DONE"
    else:
        tsData.to_csv("/mnt/data1/yuki-f/tsData_null/" + prjId + ".csv")
        return f"[{prjId}] NULL"


# スクリーンショットがあるディレクトリのパス
screenshots = "/mnt/data1/yuki-f/screenshots"
if __name__ == '__main__':
    dirs = [prjId for prjId in os.listdir(screenshots) if not prjId.startswith(".") ]
    dirs.sort()
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = executor.map(work, dirs)

        for future in futures:
            if future is not None:
                print(future)
