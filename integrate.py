#!/usr/bin/env python

import sys

filename=sys.argv[1]
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
    I+=(y1+y0)/2*(x1-x0)
    y0=y1
    x0=x1
    line=file.readline()
file.close()
print("{:.8E}".format(I))