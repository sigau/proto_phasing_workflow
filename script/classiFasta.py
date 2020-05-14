#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import sys,os,re

file=snakemake.input[0]

with open (file,"r") as contenue:
    fasta=contenue.readlines()

##global variable
nbseq=0                                             ###number of sequence in the fasta file
secseq=0                                            ### secondary counter of nbseq
new_file="result/haplotype/fasta/temp_renamed.fasta"                             ### the file after we add A and B
sort_file=snakemake.output[0]                        ### the file after we insert the B between the A
nf=open(new_file,"w")
nf.write("")
nf.close
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
        if secseq<=(nbseq/2):
            line=line[0:len(line)-1]+"_A"+"\n"       ### we add a A just before the end of line  
        else:
            line=line[0:len(line)-1]+"_B"+"\n"       ### we add a B just before the end of line 
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
