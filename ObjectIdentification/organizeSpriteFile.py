import os
import subprocess

# spritesPath = "/Users/yuki-f/Downloads/organizedSprites"
spritesPath = "/Users/yuki-f/Downloads/organizedSpritesPng"

for pathName, dirName, fileNames in os.walk(spritesPath):
    for fileName in fileNames:
        if fileName.startswith("."):
            continue

        # if ".svg" in fileName:
            #fn = fileName.rsplit(".")[len(fileName.rsplit("/")) - 1]
            # cmd = "convert \"" + pathName + "/" + fileName + "\" \"" + pathName + "/" + fn + ".png\""
            # res = subprocess.call(cmd, shell=True)
            # print(cmd)
            # continue

        if ".png" in fileName:
            continue

        os.remove(pathName + "/" + fileName)
