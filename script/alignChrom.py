#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import os 
from os.path import basename, splitext
import glob
import subprocess
file=snakemake.input[0]
file=str(file)+"*"
chrom=glob.glob(file)
output_dir=snakemake.output[0]
#print(chrom)

#print(splitext(basename(str({chrom[5]})))[0])
for i in chrom:
    #print("test")
    for j in range(0,len(chrom)):
        #print(j)
        file1=splitext(basename(str(i)))[0]
        file2=splitext(basename(str({chrom[j]})))[0]
        if (file2 == file1+"A"):          ###align ref with A
            name=str(file1)+"vs"+str(file2)
            mummer_cmd="mummer -mum -b -c " + str(i)+" "+ str(chrom[j])+" > "+str(output_dir)+"/"+ str(name)+".mums"
            mummplot_cmd="mummerplot -p "+str(output_dir)+"/"+str(name)+" --color -t postscript "+str(output_dir)+"/"+str(name)+".mums"
            subprocess.call(mummer_cmd, shell=True)
            subprocess.call(mummplot_cmd, shell=True)

        if (file2 == file1+"B"):          ###align ref with B
            name=str(file1)+"vs"+str(file2)
            mummer_cmd="mummer -mum -b -c " + str(i)+" "+ str(chrom[j])+" > "+str(output_dir)+"/"+ str(name)+".mums"
            mummplot_cmd="mummerplot -p "+str(output_dir)+"/"+str(name)+" --color -t postscript "+str(output_dir)+"/"+str(name)+".mums"
            subprocess.call(mummer_cmd, shell=True)
            subprocess.call(mummplot_cmd, shell=True)
            
        if (file1 != file2) and (file2 == file1[:-1]+"B"):  ###align A with B
            name=str(file1)+"vs"+str(file2)
            mummer_cmd="mummer -mum -b -c " + str(i)+" "+ str(chrom[j])+" > "+str(output_dir)+"/"+ str(name)+".mums"
            mummplot_cmd="mummerplot -p "+str(output_dir)+"/"+str(name)+" --color -t postscript "+str(output_dir)+"/"+str(name)+".mums"
            subprocess.call(mummer_cmd, shell=True)
            subprocess.call(mummplot_cmd, shell=True)


            

