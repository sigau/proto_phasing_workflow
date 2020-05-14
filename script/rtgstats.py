#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import subprocess
import sys
import re

input=snakemake.input[0]
output=snakemake.output[0]

nb_snp=0
nb_het_snp=0
het_level=0

############################################    use of rtg vcf-stat ###########################
command="rtg vcfstats "+ input + "> "+ output  
subprocess.call(command, shell=True)

###############################################################################################


with open(output, "r") as file:
    content=file.readlines()

cpt=0
for line in content :
    cpt=cpt+1
    if cpt==4 :
        l=line.split()
        nb_snp=l[2] 
    if cpt==13 :
        l=line.split()
        p=l[5]
        p=p[1:len(p)-1].split("/")
        nb_het_snp=p[0]

het_level=int(nb_het_snp)/int(nb_snp)


nf=open(output,"a")
nf.write(f"Heterozygosity level :   {het_level}") 
nf.close   
