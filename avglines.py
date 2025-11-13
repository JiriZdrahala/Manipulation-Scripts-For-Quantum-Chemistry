#!/usr/bin/python3

import sys

arr=[]
for line in sys.stdin:
    arr.append(float(line))
    #print(f'Processing Message from sys.stdin *****{line}*****')
print(sum(arr)/len(arr))