import os
import json
import shutil
import sys #access to command line
from subprocess import PIPE,run
#to run commands

SEARCH_PATTERN="game" #to search for
FILE_EXTENSION=".go"
COMPILE_COMMAND=["go","build"]
def findAllReqPaths(src):
    requiredPaths=[]

    for root,dirs,files in os.walk(src):
        for directory in dirs:
            if(SEARCH_PATTERN in directory.lower()):
                path=os.path.join(src,directory)
                requiredPaths.append(path)

        break
    return requiredPaths

def createDir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def getNameFromPaths(paths,strip):
    newNames=[]
    for path in paths:
        _, dir_name=os.path.split(path)
        newDirName=dir_name.replace(strip,"")
        newNames.append(newDirName)

    return newNames

def copyAndOverwrite(src,dest):
    if os.path.exists(dest):
        shutil.rmtree(dest) #delete everything within

    shutil.copytree(src,dest)#copy everything from src


def makeJsonMetadata(path,reqDirs):
    data={
        "dirNames":reqDirs,
        "numberofDirs":len(reqDirs)
    }
    with open(path,"w") as file:#auto file closing
        json.dump(data,file)

def compileCode(path):
    fileName=None

    for root,dirs,files in os.walk(path):
        for file in files:
            if file.endswith(FILE_EXTENSION):
                fileName=file
                break

        break

    if fileName is None:
        return

    cmd=COMPILE_COMMAND + [fileName]
    runCmd(cmd,path)

def runCmd(command,path):
    currWD=os.getcwd()
    os.chdir(path)

    result=run(command,stdin=PIPE,stdout=PIPE,universal_newlines=True)
    print(result)

    os.chdir(currWD)

def main(src,target):
    currWD=os.getcwd()
    src_path=os.path.join(currWD,src) #src and target and rel to cwd
    target_path=os.path.join(currWD,target)
    reqPaths=findAllReqPaths(src_path)

    newDirNames=getNameFromPaths(reqPaths,"_"+SEARCH_PATTERN)

    createDir(target_path)
    for src,dest in zip(reqPaths,newDirNames):
        dest_path=os.path.join(target_path,dest)
        copyAndOverwrite(src,dest_path)
        compileCode(dest_path)

    jsonPath=os.path.join(target_path,"metadata.json")
    makeJsonMetadata(jsonPath,newDirNames)



if __name__=="__main__":
    clArgs=sys.argv
    try:
        if len(clArgs) !=3 :
            raise Exception("Pass source and dest")
        source,target=clArgs[1:3]
        main(source,target)
    except Exception as e:
        print(e)