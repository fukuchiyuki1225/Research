import sys
import pandas as pd
import urllib.request
import time

p_ids = pd.read_csv("./metadata.csv")["p_ID"].tolist()

i = 0
for p_id in p_ids:
    print(str(i))
    try:
        url = "https://projects.scratch.mit.edu/" + str(p_id)
        savePass = "./projectJSON/" + str(p_id) + ".json"
        urllib.request.urlretrieve(url, savePass)
    except:
        pass
    i = i + 1
    time.sleep(1)