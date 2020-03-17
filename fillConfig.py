#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import os 
import glob

SR=glob.glob('data/short_reads/*')      ###create an table with the path to every file in the folder 
LR=glob.glob('data/long_reads/*')
G=glob.glob('data/genome/*')

nf=open("config.yaml","w")              ###create a config.yaml 
nf.write("short_reads:\n")
for i in range(0,len(SR)):
    nf.write(f"\tSR{i}: {SR[i]}\n")

nf.write("genome:\n")
for i in range(0,len(G)):
    nf.write(f"\tG{i}: {G[i]}\n")

nf.write("long_reads:\n")
for i in range(0,len(LR)):
    nf.write(f"\tLR{i}: {LR[i]}\n")
nf.close
