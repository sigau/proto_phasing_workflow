#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import sys, os ,csv
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqUtils import GC 
from Bio.SeqRecord import SeqRecord
import matplotlib.pyplot as plt
import numpy as np

input=[snakemake.input[0],snakemake.input[1]]
list_of_output=[]
list_of_height=[]
seq_name=[]
for file in input :
    output=file[:-6]+"_gc_content.csv"
    list_of_output.append(output)
    graph_name=output[:-3]+"svg"
    list_GC=[]
    list_id=[]

    nf=open(output,"w")
    nf.write("ID\t% GCContent\tTotal Count\tG Count\tC Count\tA Count\tT Count\tN Count\n")
    nf.close  

    seq_general=SeqRecord(Seq(""),id="all_the_genome")

    ensemble_SeqRecord= SeqIO.parse(file,'fasta')
    for sequence in ensemble_SeqRecord:
        ID=sequence.id 
        list_id.append(ID)
        myseq=sequence.seq
        gc=GC(myseq)
        list_GC.append(gc)
        nb_nucl=len(myseq)
        nb_A=myseq.count('A')
        nb_T=myseq.count('T')
        nb_G=myseq.count('G')
        nb_C=myseq.count('C')
        nb_N=myseq.count('N')

        seq_general.seq=seq_general.seq+myseq

        nf=open(output,"a")
        nf.write(f"{ID}\t{gc}\t{nb_nucl}\t{nb_G}\t{nb_C}\t{nb_A}\t{nb_T}\t{nb_N}\n")
        nf.close


    ID_G=seq_general.id 
    list_id.append(ID_G)
    myseq_G=seq_general.seq
    gc_G=GC(myseq_G)
    list_GC.append(gc_G)
    nb_nucl_G=len(myseq_G)
    nb_A_G=myseq_G.count('A')
    nb_T_G=myseq_G.count('T')
    nb_G_G=myseq_G.count('G')
    nb_C_G=myseq_G.count('C')
    nb_N_G=myseq_G.count('N')

    nf=open(output,"a")
    nf.write(f"{ID_G}\t{gc_G}\t{nb_nucl_G}\t{nb_G_G}\t{nb_C_G}\t{nb_A_G}\t{nb_T_G}\t{nb_N_G}\n")
    nf.close

    height=list_GC
    list_of_height.append(height)
    bars=list_id
    y_pos=np.arange(len(bars))

    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars , rotation=90)
    plt.ylabel('GC%')
    plt.title(f" %GC in {file} ")
    #plt.show()
    plt.savefig(graph_name,bbox_inches='tight')
    if list_id not in seq_name:
        seq_name.append(list_id)

#####versus plot#####
barWidth = 0.5


bars1=list_of_height[0]

bars2=list_of_height[1]

# The x position of bars
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]

# create bars
plt.bar(r1,bars1,width = barWidth,color='red',edgecolor = 'black',capsize=7,label='Haplotype 1')
plt.bar(r2,bars2,width = barWidth,color='blue',edgecolor = 'black',capsize=7,label='Haplotype 2')

plt.xticks([r + barWidth for r in range(len(bars1))], seq_name[0], rotation=90 )
plt.ylabel('GC%')
plt.legend()

plt.savefig(snakemake.output[4],bbox_inches='tight')