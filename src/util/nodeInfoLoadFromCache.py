import json
import os

from util.dataFolder import DataFolder


def getNodeNameFromCache():
    nodeNameList = []
    cache_dir = "../cache"

    if not os.path.exists(cache_dir):
        print("cache Folder is not exist")
        return []
    try:
        for name in os.listdir(cache_dir):
            if os.path.isdir(os.path.join(cache_dir, name)):
                nodeNameList.append(name)
        return nodeNameList

    except Exception as e:
        print(f"Error while accessing: {e}")
        return []


def createDataFolderClass(nodeNameList):
    dataFolderList = []
    for nodeName in nodeNameList:
        nodePath = "../cache"
        nodePath = os.path.join("../cache", nodeName, "path.json")
        try:
            with open(nodePath, "r", encoding="utf-8") as f:
                data = json.load(f)
                folderPath = data.get("folder_path")

                if folderPath:
                    curDataFolder = DataFolder(folderPath)
                    dataFolderList.append(curDataFolder)
        except Exception as e:
            print(f"Error while accessing: {e}")
    return dataFolderList




