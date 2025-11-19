#!/usr/bin/python3

import sys
import numpy as np

if(sys.argv.__len__()<2):
    print("USAGE: ")
    exit(1)

file=sys.argv[1]
file=open(file,'r')
lines=file.readlines()


if(sys.argv.__len__()>2):
    coeff=float(sys.argv[2])    
else:
    coeff=1.0
    
Xs=[]
Ys=[]
for line in lines:
    splitt=line.split(' ')
    Xs.append(float(splitt[0]))
    Ys.append(float(splitt[1].replace('\n','')))




avg=np.average(np.abs(Ys))
idx=0
len=len(Ys)
while idx<len:
    if(abs(Ys[idx])>avg*coeff):
        pass
        idx=idx+1
    else:
        print("{:.2f} {:.5f}".format(Xs[idx],Ys[idx]))
        idx=idx+1

exit(0)