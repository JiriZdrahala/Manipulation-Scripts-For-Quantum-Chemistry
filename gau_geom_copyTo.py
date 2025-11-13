#!/usr/bin/python3

import re
import sys
import fileinput

def IsMult_Input(input_text : str):
    pattern = re.compile(r"-?[0-9]+\s+[0-9]+", re.IGNORECASE)
    return pattern.match(input_text)

def IsMultiplicityStatement_outputfile(input_text : str):
    pattern = re.compile(r" Charge = [0-9]+ Multiplicity = [0-9]+", re.IGNORECASE)
    return pattern.match(input_text)

def IsMult_Input_ONIOM(input_text : str):
    pattern = re.compile(r"-?[0-9]+\s+[0-9]+\s+-?[0-9]+\s+[0-9]+\s+-?[0-9]+\s+[0-9]+", re.IGNORECASE)
    return pattern.match(input_text)

def isAtomDefinition_ONIOM(input_text : str):
    pattern = re.compile(r" [A-Za-z0-9]+\s+[0-9]+\s+([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))?\s+([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))?\s+([+-]?(?=\.\d|\d)(?:\d+)?(?:\.?\d*))(?:[Ee]([+-]?\d+))?\s+[A-Za-z]", re.IGNORECASE)
    return pattern.match(input_text)

def isAtomDefinition(input_text : str):
    new_text=input_text.split()
    if(len(new_text)==0): return False
    if(is_number(new_text[0])):
        new_text[0]=Num2El(new_text[0])
    if(len(new_text)==4 and not is_number(new_text[0]) and is_number(new_text[1]) and is_number(new_text[2]) and is_number(new_text[3])):
        return True
    else:
        return False

def El2Num(El=""):
    if(not El.isnumeric()):
        return elements.index(str.strip(El))+1
    else:
        return El

def Num2El(El=""):
    if(El.isnumeric()):
        return elements[int(El)-1]
    else:
        return El

#TODO, possible off by one error
def file_forwards(file,num):
    for i in range(1,num):
        file.readline()    

def file_gotoLine(file,num):
    file.seek(0,0)
    file_forwards(file,num)

        
#what the f bro, i've googled extensively for a good way to do this, and this is the way that is ACCEPTED by the community?!! Exception catching?
def is_number(s:str):
    try:
        float(s)
        return True
    except ValueError:
        return False


if len(sys.argv) < 3 :
    print('Overwrites first Gaussian geometry in an input file. Either last "Input orientation" from an output file or last geometry from an input file.')
    print('Does not account for isotopes.')
    print('USAGE: gau_geom_copyTo.py (.inp/.out) (.inp)')
    exit()

elements = [ 'H','He','Li','Be','B','C','N','O','F','Ne', \
             'Na','Mg','Al','Si','P','S','Cl','Ar', \
             'K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn',\
                      'Ga','Ge','As','Se','Br','Kr',\
             'Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd',\
                      'In','Sn','Sb','Te','I','Xe',\
             'Cs','Ba','La',\
                           'Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho',\
                           'Er','Tm','Yb','Lu',\
             'Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg',\
                       'Tl','Pb','Bi','Po','At','Rn',\
             'Fr','Ra','Ac']



old_geometry=[]
old_geometry_lines=[]
geometry_start=-1


inputfile = open(sys.argv[2],"r")


line = inputfile.readline()
i=1

isOniom=False
HLEnd = -1 #High Layer End
j=0

while line:
    if IsMult_Input_ONIOM(line):
        isOniom=True
        oldChAndMul=line.split()
        geometry_start=i+1
        line = inputfile.readline()
        while isAtomDefinition_ONIOM(line):
            strr=line.split()
            old_geometry.append(strr[0])
            old_geometry_lines.append(strr)
            if(strr[5].upper()=='L' and HLEnd == -1):
                HLEnd=j
            line=inputfile.readline()
            j+=1
        break
    elif IsMult_Input(line):
        oldChAndMul=line.split()
        geometry_start=i+1
        line = inputfile.readline()
        while line:
            if isAtomDefinition(line):
                strr=line.split()
                
                old_geometry.append(strr[0])
                line=inputfile.readline()
            else:
                break
        break
    else:
        line=inputfile.readline()
        if(line==""):
            print('Could not find -- Input file geometry -- in: ' + sys.argv[2])
            exit()
        i=i+1
old_geometry_atomcount=len(old_geometry)
inputfile.seek(0)
inputfile_lines=inputfile.readlines()
for i in range(0,old_geometry_atomcount):
    inputfile_lines.pop(geometry_start-1)
inputfile.close()
file = open(sys.argv[1],"r")
differentGeometry=False

if '.out' in sys.argv[1].lower() or '.log' in sys.argv[1].lower() :
    if(len(sys.argv)==4 and (sys.argv[3]).lower()=="standard"):
        find_geometry="Standard orientation"
    else:
        find_geometry="Input orientation:"
    new_geometry=[]
    line = file.readline()
    while line:
        if(find_geometry in line):
            new_geometry.clear()
            line = file.readline()
            line = file.readline()
            line = file.readline()
            line = file.readline()
            while line:
                line = file.readline()
                if('---------------' not in line):
                    atom=line.split()
                    atom[1]=Num2El(atom[1])
                    arr=[atom[1],atom[3],atom[4],atom[5]]
                    new_geometry.append(arr)
                else:
                    break
        else:
            line=file.readline()
            if(line=="" and len(new_geometry) == 0):
                print('Could not find -- '+find_geometry + ' -- in: ' + sys.argv[1])
                exit()
    
    # for i in range(len(new_geometry)):
    #     if(len(new_geometry) != len(old_geometry) or new_geometry[i][0] != (old_geometry[i])):
    #         print('Differing elements in geometries')
    #         print('Continue?')
    #         inp=input().capitalize()
    #         if(inp=="\n" or inp[0] == "Y"):
    #             differentGeometry=True
    #             break
    #         else:
    #             exit()
    
    for i in range(len(new_geometry)):
        new_geometry[i][0]=Num2El(new_geometry[i][0])
        for j in range(1,4):
            new_geometry[i][j]=" "+new_geometry[i][j]
        if(isOniom):
            HL="L"
            if(i<HLEnd):
                HL="H"
                
            new_geometry[i]="{ele:>3} 0 {x:>15} {y:>15} {z:>15} {HL:>1}\n".format(ele=new_geometry[i][0],x=(new_geometry[i][1]),y=(new_geometry[i][2]),z=(new_geometry[i][3]),HL=HL)
        else:
            new_geometry[i]="{ele:>3} {x:>15} {y:>15} {z:>15}\n".format(ele=new_geometry[i][0],x=(new_geometry[i][1]),y=(new_geometry[i][2]),z=(new_geometry[i][3]))
        inputfile_lines.insert(geometry_start-1+i,new_geometry[i])
    
    
    for line in inputfile_lines:
        print(line,end='')
elif '.inp' in sys.argv[1].lower() or '.gjf' in sys.argv[1].lower() :
    line = file.readline()
    new_geometry=[]
    while line:
        if IsMult_Input(line):           
            line = file.readline()
            while line:
                if isAtomDefinition(line):
                    strr=line.split()
                    new_geometry.append(strr)
                    line = file.readline()
                else:
                    break
            break
        else:
            line=file.readline()
    # for i,line in enumerate(new_geometry):
    #     if(line[0]!=(old_geometry[i])):
    #         print('Differing elements in geometries')
    #         print('Continue?')
    #         inp=input().capitalize()
    #         if(inp=="" or inp[0] == "Y"):
    #             pass
    #         else:
    #             break
    #inputfile=open(sys.argv[2],"w")
    
    #newline=inputfile.readline()
    for i in range(len(new_geometry)):
        new_geometry[i][0]=Num2El(new_geometry[i][0])
        for j in range(1,4):
            new_geometry[i][j]=" "+new_geometry[i][j]
            
        if(isOniom):
            HL="L"
            if(i<HLEnd):
                HL="H"
            new_geometry[i]="{ele:>3} 0 {x:>15} {y:>15} {z:>15} {HL:>2}\n".format(ele=new_geometry[i][0],x=(new_geometry[i][1]),y=(new_geometry[i][2]),z=(new_geometry[i][3]),HL=HL)
        else:
            new_geometry[i]="{ele:>3} {x:>15} {y:>15} {z:>15}\n".format(ele=new_geometry[i][0],x=(new_geometry[i][1]),y=(new_geometry[i][2]),z=(new_geometry[i][3]))
        #new_geometry[i]=str(new_geometry[i]).replace(",","").replace("'","").replace("[","").replace("]","")+"\n"
        #inputfile_lines.pop(geometry_start-1+i)
        inputfile_lines.insert(geometry_start-1+i,new_geometry[i])
    for line in inputfile_lines:
        #inputfile.write(line)
        print(line,end='')
    #inputfile.close()
pass
