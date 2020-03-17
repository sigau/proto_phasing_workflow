#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import sys

file=sys.argv[1]

cptP=0
cptV=0
cptT=0
#T=0

with open(file,"r") as contenue:
    vcf=contenue.readlines()

for line in vcf :
    if line[0]!="#" :
        #T=T+1
        for i in range(0, len(line)-1):
            if line[i]=="|" and i>20:
                cptP=cptP+1
            if line[i] == "/" :
                cptV=cptV+1

cptT=cptP+cptV

print(f"we got {cptP} phased genotypes, {cptV} unphased genotypes and a total of {cptT} variants")
#print(T)