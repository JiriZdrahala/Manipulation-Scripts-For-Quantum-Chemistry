#!/usr/bin/python3

import re
import sys
import os

path=os.getcwd()
outfiles=sys.argv[1:]
outfiles_c=len(outfiles)


for file in outfiles:
    w=0.0
    inten=0.0
    
    openedFile=open(file,'r')
    curPos=openedFile.tell()
    line=openedFile.readline()
    while(line):
        
        #if(line[1:3]=='w='):
        #    lineNumSplit=line.split(' ')
        #    w=round(45.5640/float(lineNumSplit[5]),2)
        if(line[38:45]=='[Alpha]'):
            #AlphaIdx=line.find(r"[Alpha]")
            #NumIdx=line.find('=',AlphaIdx+5)+2
            #line=" ".join(line.split())
            #lineNum=line[NumIdx:len(line)]
            #lineNumSplit=line.split(' ')
            inten=float(line[59:70])
            w=float(line[47:53])/10.0
            print("{:.2f} {:.5f}".format(w,inten))
        curPos=openedFile.tell()
        line=openedFile.readline()
        
    openedFile.close()
    #print("{:.2f} {:.5f}".format(w,inten))