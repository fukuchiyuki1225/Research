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

for block in blocks:
    for obj in block:
        print(block[obj]["opcode"])