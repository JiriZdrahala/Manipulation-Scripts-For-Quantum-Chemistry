#!/usr/bin/env python3
import re
import sys

if(len(sys.argv)<1):
    print("USAGE:")
    print()
    exit(1)
fileName='FILE.INP'
file=open(fileName,'r')

numInFile=int(sys.argv[1])

line=file.readline()
CollectedLines=[]
num=0
fileCount=0
while(line):
    if("--link1--" in line.lower()):
        num+=1
        fileCount+=1
    if(num % numInFile == 0 and num != 0):
        newFileName=fileName.replace(".INP","_"+str(fileCount)+".inp")
        newFile=open(newFileName,'w')
        newFile.writelines(CollectedLines)
        newFile.close()
        CollectedLines=[]
        line=file.readline()
        num=0
        continue
    CollectedLines.append(line)
    line=file.readline()

if(len(CollectedLines)>0):
    num+=1
    fileCount+=1
    newFileName=fileName.replace(".INP","_"+str(fileCount)+".inp")
    newFile=open(newFileName,'w')
    newFile.writelines(CollectedLines)
    newFile.close()

file.close()