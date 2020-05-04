#!/usr/bin/env python3 
# -*- coding: utf-8 -*

import sys, os
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqUtils import GC 
from Bio.SeqRecord import SeqRecord

input=snakemake.input[0]
output=snakemake.output[0]

nf=open(output,"w")
nf.write("ID\t% GCContent\tTotal Count\tG Count\tC Count\tA Count\tT Count\n")
nf.close  

seq_general=SeqRecord(Seq(""),id="all_the_genome")

ensemble_SeqRecord= SeqIO.parse(input,'fasta')
for sequence in ensemble_SeqRecord:
    ID=sequence.id 
    myseq=sequence.seq
    gc=GC(myseq)
    nb_nucl=len(myseq)
    nb_A=myseq.count('A')
    nb_T=myseq.count('T')
    nb_G=myseq.count('G')
    nb_C=myseq.count('C')

    seq_general.seq=seq_general.seq+myseq

    nf=open(output,"a")
    nf.write(f"{ID}\t{gc}\t{nb_nucl}\t{nb_G}\t{nb_C}\t{nb_A}\t{nb_T}\n")
    nf.close


ID_G=seq_general.id 
myseq_G=seq_general.seq
gc_G=GC(myseq_G)
nb_nucl_G=len(myseq_G)
nb_A_G=myseq_G.count('A')
nb_T_G=myseq_G.count('T')
nb_G_G=myseq_G.count('G')
nb_C_G=myseq_G.count('C')

nf=open(output,"a")
nf.write(f"{ID_G}\t{gc_G}\t{nb_nucl_G}\t{nb_G_G}\t{nb_C_G}\t{nb_A_G}\t{nb_T_G}\n")
nf.close

