#!/usr/bin/env python3

import sys
import re

file=open(sys.argv[1],'r')
lines=file.readlines()

for (index,line) in enumerate(lines):
    idx=line.find('$') 
    if(idx>-1):
        line=line[0:idx]+' '+line[idx+1:len(line)]
        lines[index]=line
        lines[index-1]=(lines[index-1])[0:len(lines[index-1])-1] + ' &\n'


for line in lines:
    print(line,end='')