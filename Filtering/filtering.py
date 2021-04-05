import json
import os
import pandas as pd
import cv2

filePass = "/Users/yuki-f/Documents/SocSEL/Research/Filtering/projectJSON/"

df = pd.DataFrame(columns=["id"])

jsonFiles = os.listdir(filePass)

fileNames = []

for jsonFile in jsonFiles:
    fileNames.append(jsonFile.split(".")[0])

for prjId in fileNames:
    try:
        with open(filePass + prjId + ".json") as f:
            data = json.load(f)
    except Exception as e:
        continue

    targets = data["targets"]
    blocks = []

    for target in targets:
        if len(target["blocks"]) == 0:
            continue
        blocks.append(target["blocks"])

    roopFlag = False
    eventFlag = False
    motionFlag = False

    try:
        for block in blocks:
            for obj in block:
                blockName = block[obj]["opcode"]
                if blockName == "control_forever":
                    roopFlag = True
                    break
                if blockName == "event_whenkeypressed" or blockName == "event_whenthisspriteclicked" or blockName == "event_whenbroadcastreceived":
                    eventFlag = True
                    break
                if blockName.startswith("motion"):
                    motionFlag = True
    except Exception as e:
        continue

    if roopFlag == False and eventFlag == False and motionFlag == True:
        df = df.append(pd.DataFrame(data=[[prjId]],columns=["id"]))
        
df.to_csv("./filterd_cat.csv")