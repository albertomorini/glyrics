import os
import sys
import platform
import json
import hashlib

def serialize_JSON(folder, filename, data):
    with open(f"{folder}/{filename}", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
#da Json a dicts

#dato un JSON restituisco un dict(dizionario{})
def read_JSON(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf8") as file:
            data = json.load(file)
            return data
    else:
        return None #if doesn't exists i create a file configuration


def serializeSet(folder,filename,data):
    with open(f"{folder}/{filename}","w",encoding='utf-8') as f:
        f.write(str(data))

def readSet(path):
    try:
        f = open(path,"r")
        text = f.read()
        f.close()

        text = text.replace("{","").replace("}","").replace("'","").replace(" ","")
        text = text.split(",")

        bfrSet = set()
        for i in text:
            bfrSet.add(i)

        return bfrSet
    except Exception as e: #if doesn't exists return a new set
        return set()


def getDiffMD5(obj1,obj2):
    hash1 = hashlib.md5(obj1.encode()).hexdigest()
    hash2 = hashlib.md5(obj2.encode()).hexdigest()
    return hash1==hash2

def getDiffDict(dict1, dict2):
    if(dict1.items() == dict2.items()):
        return True
    elif(dict1.keys() == dict2.keys()):
        #different values
        for i in dict1:
            if(dict1[i]!=dict2[i]):
                return "at key: "+str(i) + (str(dict1[i])+"\t\t"+str(dict2[i]))
    else:
        #different keys
        maxDic = max(len(dict1),len(dict2))
        while maxDic>0:
            maxDic-=1
            tmp1=dict1.popitem()
            tmp2=dict2.popitem()
            if(tmp1[0]!=tmp2[0]):
                return (str(tmp1) + "\t\t" +str(tmp2))




def doHashMD5(pathFile):
    result = hashlib.md5(pathFile.encode())

    return result.hexdigest()

'''
TO IMPORT:

sys.path.insert(0, '../+utility/')
import python_utility as pyut
'''
