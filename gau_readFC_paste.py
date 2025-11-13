#!/usr/bin/env python

import re
import sys


def FindSubstrings(arr : list[str], substr : str, start:int = 0) -> list[int]:
    idxs=[]
    for i in range(start,len(arr),1):
        if(substr in arr[i]):idxs.append(i)
    return idxs

def IndexSubstring(arr : list[str],substr : str, start:int=0) -> int:
    for i in range(start,len(arr),1):
        if(substr in arr[i]):return i
    return -1

argc=len(sys.argv)-1
if(argc<2):
    print("USAGE")
    exit(1)

origTDFreqFileName=sys.argv[1]
origTDFreqFile=open(origTDFreqFileName,'r')
lines=origTDFreqFile.readlines()
origTDFreqFile.close()
origTDFreqFile=open(origTDFreqFileName,'w')
idxs=FindSubstrings(lines,' Cartesian Nonad. Coup.:  Max')

startIdx=idxs[1]
startBeforeIdx=IndexSubstring(lines,'----',startIdx)-1


readFCFile=sys.argv[2]
readFCFile=open(readFCFile,'r')
line=readFCFile.readline()
while(not 'Electronic transition elements' in line):
    line=readFCFile.readline()

lines.insert(startBeforeIdx," Electronic transition elements\n")
startBeforeIdx+=1
line=readFCFile.readline()
while(not '---' in line):
    lines.insert(startBeforeIdx,line)
    startBeforeIdx+=1
    line=readFCFile.readline()

pass
origTDFreqFile.writelines(lines)
origTDFreqFile.close()
