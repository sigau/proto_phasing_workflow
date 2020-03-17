#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import sys,os,re

file=sys.argv[1]

with open (file,"r") as contenue:
    fasta=contenue.readlines()

##global variable
nbseq=0                                             ###number of sequence in the fasta file
secseq=0                                            ### secondary counter of nbseq
new_file="rename_"+file                             ### the file after we add A and B
sort_file="sorted_"+new_file                        ### the file after we insert the B between the A

##count the number of sequence
position_of_chevron=[]
cpt_chevron=-1
for line in fasta :
    cpt_chevron=cpt_chevron+1
    if line[0]==">":
        nbseq=nbseq+1
        position_of_chevron.append(cpt_chevron)                      ###we spot where are the chevron and so
                                                                     ###where the sequence begin and end

### first step rename the sequence with identical name
for line in fasta :
    if line[0]==">" :
        secseq=secseq+1
        pipeCPT=0
        wip=0  ##where is pipe  
        while (pipeCPT!=2) :
            for i in range (0, len(line)-1):
                if line[i]=="|" :
                    pipeCPT=pipeCPT+1
                    wip=i
        if secseq<=(nbseq/2):
            line=line[0:wip-1]+"A"+line[wip:len(line)-1]+"\n"       ### we add a A just before the second pipe
        else:
            line=line[0:wip-1]+"B"+line[wip:len(line)-1]+"\n"       ### we add a B just before the second pipe
    
        nf=open(new_file,"a") 
        nf.write(line)
        nf.close     

    else :
        nf=open(new_file,"a") 
        nf.write(line)
        nf.close

nf=open(new_file,"a")
nf.write("\n")
nf.close  


### sort the new file (insert the B between the A)

with open(new_file,"r") as contenue2:
    renamed=contenue2.readlines()

position_of_chevron.append(len(renamed))                        ###we add the position of the last line from the file to have all the 

k=0                                                         ### will be use as position of chevron 's indice 
nc=0                                                        ### will say how many seq we already copy
nf=open(sort_file,"w")
while (nc<len(position_of_chevron)-1):
    for j in range (0,len(position_of_chevron)-1):
        if k==j :
            for i in range(position_of_chevron[j], position_of_chevron[j+1]):
                nf.write(renamed[i])
                
            nc=nc+1

            if j<(len(position_of_chevron)-1)/2:                #if we are at the first half of the file (ex : chromosome 1A)
                k=k+((len(position_of_chevron)-1)/2)            #we go to the second half to get the second chromosome (ex : chromosome 1B)
            else :                                              #if we are at the second half of the file (ex : chromosome 1B)
                k=k-((len(position_of_chevron)-1)/2)+1          #we go back to the first half to get the next chromosome (ex : chromosome 2A)

nf.close
os.remove(new_file)
