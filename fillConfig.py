#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import os 
from os.path import basename, splitext
import glob

SR=glob.glob('data/short_reads/*')      ###create an table with the path to every file in the folder 
LR=glob.glob('data/long_reads/*')
G=glob.glob('data/genome/*')

nf=open("config.yaml","w")              ###create a config.yaml 
nf.write("short_reads:\n")
for i in range(0,len(SR)):
    SR_filename=splitext(basename(str({SR[i]})))[0]
    SR_filename=splitext(basename(str(SR_filename)))[0]    ###if the file haven't been compress comment this line 
    nf.write(f" {SR_filename}: {SR[i]}\n")

nf.write("genome:\n")
for i in range(0,len(G)):
    G_filename=splitext(basename(str({G[i]})))[0]
    #G_filename=splitext(basename(str(G_filename)))[0]      ###if the file have been compress comment this line 
    nf.write(f" {G_filename}: {G[i]}\n")

nf.write("long_reads:\n")
for i in range(0,len(LR)):
    LR_filename=splitext(basename(str({LR[i]})))[0]
    #LR_filename=splitext(basename(str(LR_filename)))[0]      ###if the file have been compress comment this line 
    nf.write(f" {LR_filename}: {LR[i]}\n")
nf.close
