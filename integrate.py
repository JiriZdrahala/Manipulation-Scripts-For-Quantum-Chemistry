#!/usr/bin/env python

import sys
import math

argc=len(sys.argv)-1
filename=sys.argv[1]
fromx=float(sys.argv[2])
tox=float(sys.argv[3])
roa=False
if(argc>=4):
    if(sys.argv[4].lower()=='t'):roa=True

file=open(filename,'r')
line=file.readline()
ls=line.split()
x0=float(ls[0])
y0=float(ls[1])
I=0
line=file.readline()
while(line):
    ls=line.split()
    x1=float(ls[0])
    y1=float(ls[1])
    
    if(x0>fromx and x1<tox):
        if(roa):
            I+=(y1*y1+y0*y0)/2*(x1-x0)
        else:
            I+=(y1+y0)/2*(x1-x0)
    y0=y1
    x0=x1
    line=file.readline()
file.close()
if(roa):I=math.sqrt(I)
print("{:.8E}".format(I))