import json

fileName = "./sample.json"

with open(fileName) as f:
    data = json.load(f)

targets = data["targets"]
blocks = []

for target in targets:
    if len(target["blocks"]) == 0:
        continue
    blocks.append(target["blocks"])

roopFlag = False
eventFlag = False
motionFlag = False

for block in blocks:
    for obj in block:
        blockName = block[obj]["opcode"]
        if blockName == "control_forever":
            roopFlag = True
            break
        if blockName == "event_whenflagclicked" or blockName == "event_whenkeypressed" or blockName == "event_whenthisspriteclicked":
            eventFlag = True
            break
        if blockName.startswith("motion"):
            motionFlag = True

if roopFlag == True or eventFlag == True or motionFlag == False:
    print("jogai")
        