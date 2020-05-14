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
            name=str(file1)+"VS"+str(file2)
            mummer_cmd="mummer -mum -b -c " + str(i)+" "+ str(chrom[j])+" > "+str(output_dir)+"/"+ str(name)+".mums"
            mummplot_cmd="mummerplot -p "+str(output_dir)+"/"+str(name)+" --color -t postscript "+str(output_dir)+"/"+str(name)+".mums"
            dnadiff_cmd="dnadiff --prefix "+str(output_dir)+"/"+str(name)+" "+ str(i)+" "+ str(chrom[j])
            subprocess.call(mummer_cmd, shell=True)
            subprocess.call(mummplot_cmd, shell=True)
            subprocess.call(dnadiff_cmd, shell=True)
        if (file2 == file1+"B"):          ###align ref with B
            name=str(file1)+"VS"+str(file2)
            mummer_cmd="mummer -mum -b -c " + str(i)+" "+ str(chrom[j])+" > "+str(output_dir)+"/"+ str(name)+".mums"
            mummplot_cmd="mummerplot -p "+str(output_dir)+"/"+str(name)+" --color -t postscript "+str(output_dir)+"/"+str(name)+".mums"
            dnadiff_cmd="dnadiff --prefix "+str(output_dir)+"/"+str(name)+" "+ str(i)+" "+ str(chrom[j])
            subprocess.call(mummer_cmd, shell=True)
            subprocess.call(mummplot_cmd, shell=True)
            subprocess.call(dnadiff_cmd, shell=True)
        if (file1 != file2) and (file2 == file1[:-1]+"B"):  ###align A with B
            name=str(file1)+"VS"+str(file2)
            mummer_cmd="mummer -mum -b -c " + str(i)+" "+ str(chrom[j])+" > "+str(output_dir)+"/"+ str(name)+".mums"
            mummplot_cmd="mummerplot -p "+str(output_dir)+"/"+str(name)+" --color -t postscript "+str(output_dir)+"/"+str(name)+".mums"
            dnadiff_cmd="dnadiff --prefix "+str(output_dir)+"/"+str(name)+" "+ str(i)+" "+ str(chrom[j])
            subprocess.call(mummer_cmd, shell=True)
            subprocess.call(mummplot_cmd, shell=True)
            subprocess.call(dnadiff_cmd, shell=True)

#####create a recap file with the average identity of each sequence againts the others sequence 
path_reports=[]
for element in os.listdir(output_dir):
    if element.endswith('.report'):
        path_reports.append(output_dir+str(element))


recap="result/haplotype/fasta/dnadiff/recap.csv"
nf=open(recap,"w")
nf.write("")
nf.close

full_seq_report=[]
for element in os.listdir("result/haplotype/fasta/dnadiff/") :
    if element.endswith('.report'):
        full_seq_report.append("result/haplotype/fasta/dnadiff/"+str(element))

for report in full_seq_report:
    with open(report,"r") as fiel:
        info=fiel.readlines()
        identity=info[18]
        identity=identity.split()
        file_name=report.split("/")
        file_name=file_name[4].split("VS")
        seq2=file_name[1].split(".")
        nf=open(recap,"a")
        nf.write(f"{file_name[0]}\t{seq2[0]}\t{identity[1]}\n")
        nf.close

for report in path_reports:
    with open(report,"r") as fiel:
        info=fiel.readlines()
        identity=info[18]
        identity=identity.split()
        file_name=report.split("/")
        file_name=file_name[4].split("VS")
        seq2=file_name[1].split(".")
        nf=open(recap,"a")
        nf.write(f"{file_name[0]}\t{seq2[0]}\t{identity[1]}\n")
        nf.close
        #print(f"{file_name[4]}\t{identity[0]}\t{identity[1]} ")


#####sort the recap file for easy reading######
with open(recap,"r") as re :
    content=re.readlines()
    #print(f"1 {content} ")
    content.sort()
    #print(f"2 {content} ")
    nf=open(recap,"w")
    nf.write("Sequence 1\tSequence 2\tAvgIdentity\n")
    nf.close
    #print(f"3 {content} ")
    for i in content:
        nf=open(recap,"a")
        nf.write(i)
        nf.close

