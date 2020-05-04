
configfile: "config.yaml"

SR_ext=".fastq.gz"
#SR_ext=input("short-reads extension : a for '.fastq' or b for '.fastq.gz' ? ")
#if SR_ext=="a" :
    #SR_ext=".fastq"
#else :
    #SR_ext=".fastq.gz"
LR_ext=".fastq"
#LR_ext=input("long-reads extension : a for '.fastq' or b for '.fastq.gz' ? ")
#if LR_ext=="a" :
    #LR_ext=".fastq"
#else :
    #LR_ext=".fastq.gz"
#sample_name=input("sample name : ")
sample_name="sample"
#library=input("library used for Short Read : ")
library="library"
#platform=input("platform (e.g. illumina, solid) : ")
platform="illumina"
#unit=input("platform unit (eg. run barcode) : ")
unit="X"


## one rule to rule them all
rule all:
    input:
        plot="result/plots/"+sample_name+".gp",
        txt="data/variant-called/ShortReads/"+sample_name+"SR_stats.txt",
        chrom=directory("result/haplotype/fasta/chrom_align/"),
        csv1="result/haplotype/fasta/"+sample_name+"haplotype_1_gc_content.csv",
        csv2="result/haplotype/fasta/"+sample_name+"haplotype_2_gc_content.csv"
        #htmlSR=expand("quality_control/short_reads/{short}_fastqc.html", short=config["short_reads"]),
        #htmlLR="quality_control/long_reads/NanoPlot-report.html"


################################################## Quality control ######################################################################################
rule QC:
    input:
        htmlSR=expand("quality_control/short_reads/{short}_fastqc.html", short=config["short_reads"]),
        htmlLR="quality_control/long_reads/NanoPlot-report.html"
        
rule QC_SR:
    input:
        SR=expand("data/short_reads/{short}"+SR_ext , short=config["short_reads"])
    output:
        html=expand("quality_control/short_reads/{short}_fastqc.html", short=config["short_reads"])
    shell:
        "fastqc -o quality_control/short_reads/ {input.SR}"
        "&& firefox {output.html}"
        
rule QC_LR:
    input:
        LR=expand("data/long_reads/{long}"+LR_ext, long=config["long_reads"])
    output:
        html="quality_control/long_reads/NanoPlot-report.html"
    threads : 10
    params:
        barcode="--barcoded", ###Use if you want to split the summary file by barcode
        N50="--N50", ###Show the N50 mark in the read length histogram
        rich="--fastq_rich",     ###Data is in one or more fastq file(s) generated by albacore, MinKNOW or guppy
                    #with additional information concerning channel and time.
        format="svg"### Specify format for output {eps,jpeg,jpg,pdf,pgf,png,ps,raw,rgba,svg,svgz,tif,tiff}
    shell:
        "NanoPlot -t {threads} {params.N50} {params.rich} {input} -o quality_control/long_reads/ -f {params.format}"
        " && firefox {output.html}"

################################################## Manipulation on the SHORT-READS ######################################################################################

rule index_fasta:          ### Indexing the reference sequence
    input:
        fa=expand("data/genome/{genome}.fasta", genome=config["genome"])
    output:
        amb=expand("data/genome/{genome}.fasta.amb", genome=config["genome"]),
        ann=expand("data/genome/{genome}.fasta.ann", genome=config["genome"]),
        bwt=expand("data/genome/{genome}.fasta.bwt", genome=config["genome"]),
        pac=expand("data/genome/{genome}.fasta.pac", genome=config["genome"]),
        sa=expand("data/genome/{genome}.fasta.sa", genome=config["genome"]),
        dic=expand("data/genome/{genome}.dict", genome=config["genome"])
    shell:
        "bwa index {input.fa}" 
        "&& picard CreateSequenceDictionary R={input.fa} O={output.dic}" 
        "&& samtools faidx {input.fa}"

rule bwa_aln:           ###align the reads with the reference fasta  
    input:
        fa=expand("data/genome/{genome}.fasta", genome=config["genome"]),
        SR=expand("data/short_reads/{short}"+SR_ext , short=config["short_reads"]),
        sa=expand("data/genome/{genome}.fasta.sa", genome=config["genome"])  #just for doing it after index_fasta
    output:
        "data/aligned_read/short_reads/sam_file/"+sample_name+".sam"
    log:
        "log/bwa_mem/"+sample_name+".log"
    threads: 8
    shell:
        "(bwa mem -M -t {threads} {input.fa} {input.SR} > {output}) 2> {log}"   ###-M parameter for mapping to mark which alignments are primary and which are secondary

rule sam_to_bamSR:           ### compressed to BAM 
    input:
        "data/aligned_read/short_reads/sam_file/"+sample_name+".sam"
    output:
        "data/aligned_read/short_reads/bam_file/"+sample_name+".bam"
    log:
        "log/samtools_view/sam_to_bam/"+sample_name+".log"
    threads: 10
    shell:
        "(samtools view -@ {threads} -Sb {input} > {output}) 2> {log}"

rule sort_bamSR:          ### sort the bam (needed for variant calling)
    input:
        "data/aligned_read/short_reads/bam_file/"+sample_name+".bam"
    output:
        "data/aligned_read/short_reads/sorted_bam/"+sample_name+"_SORTED.bam"
    log:
        "log/samtools_sort/"+sample_name+"SR.log"
    threads: 10
    shell:
        "(samtools sort -@ {threads} {input} -o {output}) 2> {log}"

rule mapped_bam:        ### getting only the mapped reads
    input:
        "data/aligned_read/short_reads/sorted_bam/"+sample_name+"_SORTED.bam"
    output:
        "data/aligned_read/short_reads/mapped_bam/"+sample_name+"_SORTED_mapped.bam"
    log:
        "log/samtools_view/mapped_bam/"+sample_name+".log"
    threads: 10
    shell:
        "(samtools view -@ {threads} -b -f 2 {input} > {output}) 2> {log}"

rule picard_markduplicates:    ###mark the duplicated reads  
#Duplicates can arise during sample preparation e.g. library construction using PCR or
#result from a single amplification cluster, incorrectly detected as multiple clusters 
#by the optical sensor of the sequencing instrument
    input:
        "data/aligned_read/short_reads/mapped_bam/"+sample_name+"_SORTED_mapped.bam"
    output:
        bam="data/aligned_read/short_reads/mark_bam/"+sample_name+"_markduplicated.bam",
        txt="data/markduplicated_metrics/"+sample_name+"markduplicates_metric.txt"
    log:
        "log/picardtools/"+sample_name+"_markduplicated.log"
    shell:
        "(picard MarkDuplicates I={input} O={output.bam} M={output.txt}) 2> {log}"

rule picard_AddOrRep:   ### Add read group needed for gatk (and create bam index)
    input:
        "data/aligned_read/short_reads/mark_bam/"+sample_name+"_markduplicated.bam"
    output:
        "data/aligned_read/short_reads/readyToCall/"+sample_name+"_ok.bam"
    log:
        "log/picardtools/"+sample_name+"-AddOrReplaceReadGroups.log"
    params:
        SM=sample_name , #SM = sample name 
        LB=library ,    #LB = library used for Short Read
        PL=platform ,   #PL = latform (e.g. illumina, solid) 
        PU=unit ,       #PU = platform unit (eg. run barcode)
    shell:
        "(picard AddOrReplaceReadGroups I={input} O={output} SM={params.SM} LB={params.LB} PL={params.PL} PU={params.PU} CREATE_INDEX=True) 2>{log}"

rule gatk_haplo:    ### Variant calling (short reads) 
    input:
        bam="data/aligned_read/short_reads/readyToCall/"+sample_name+"_ok.bam",
        ref=expand("data/genome/{genome}.fasta", genome=config["genome"])
    output:
        "data/variant-called/ShortReads/"+sample_name+"SR.vcf"
    log:
        "log/gatk/"+sample_name+".log"
    shell:
        "(gatk HaplotypeCaller -I {input.bam} -R {input.ref} -O {output})"


##################################### POSSIBLE OPTION FOR GATK HAPLOTYPECALLER ###################################################################################
#                                                                                                                                                                #
#    ## --ploidy:Integer (by default the programme put 2 for diploidy)                                                                                           #
#    ## --base-quality-score-threshold (by default the programme put 18)                                                                                         #
#    ## --min-base-quality-score (Minimum base quality required to consider a base for calling by default 10)                                                    #
#    ##automatically applied filter :                                                                                                                            #
#                                                                                                                                                                #
#    #NotSecondaryAlignmentReadFilter : Filter out reads representing secondary alignments                                                                       #
#    #GoodCigarReadFilter : Keep only reads containing good CIGAR string (https://gatk.broadinstitute.org/hc/en-us/articles/360037593371-GoodCigarReadFilter)    #
#    #NonZeroReferenceLengthAlignmentReadFilter : Filter out reads that do not align to the reference                                                            #
#    #PassesVendorQualityCheckReadFilter : Filter out reads failing platfor/vendor quality checks                                                                #
#    #MappedReadFilter : Filter out unmapped reads (https://gatk.broadinstitute.org/hc/en-us/articles/360037592551-MappedReadFilter)                             #
#    #MappingQualityAvailableReadFilter : Median mapping quality of reads supporting each allele (MMQ)                                                           #
#    #NotDuplicateReadFilter : Filter out reads marked as duplicate                                                                                              #
#    #MappingQualityReadFilter : Median mapping quality of reads supporting each allele                                                                          #
#    #WellformedReadFilter : Keep only reads that are well-formed (https://gatk.broadinstitute.org/hc/en-us/articles/360037591691-WellformedReadFilter)          #
#                                                                                                                                                                #
##################################################################################################################################################################

rule vcf_stats:    
    input:
        "data/variant-called/ShortReads/"+sample_name+"SR.vcf"
    output:
        txt="data/variant-called/ShortReads/"+sample_name+"SR_stats.txt",
    script:
        "script/rtgstats.py"


################################################## Manipulation on the LONG-READS ######################################################################################

rule merge_LR:      ###Merging the long reads into one file (more practical for nanochop)
    input:
        LR=expand("data/long_reads/{long}"+LR_ext, long=config["long_reads"]),
        sa=expand("data/genome/{genome}.fasta.sa", genome=config["genome"])
    output:
        "data/long_reads/merged/"+sample_name+"_LR_merged"+LR_ext
    shell:
        "cat {input.LR} > {output}"

rule trim_pore:     ###searching and triming adapter in long reads 
    input:
        "data/long_reads/merged/"+sample_name+"_LR_merged"+LR_ext
    output:
        "data/long_reads/trim/"+sample_name+"_LR_trim"+LR_ext
    log:
        "log/porechop/"+sample_name+".log"
    threads:10
    shell:
        "(porechop -t {threads} -i {input} -o {output}) 2> {log}"

rule map_LR:        ### Mapping the long reads with the reference 
    input:
        LR="data/long_reads/trim/"+sample_name+"_LR_trim"+LR_ext ,
        ref=expand("data/genome/{genome}.fasta", genome=config["genome"])

    output:
        "data/aligned_read/long_reads/sam_file/"+sample_name+"_LR.sam"
    log:
        "log/minimap2/"+sample_name+".log"
    params:
        p="map-ont"  ### if using nanopore vs reference mapping
        #p="map-pb"  ###if using Pacbio vs reference mapping
    threads: 8
    shell:
        "(minimap2 -t {threads} -ax {params.p} {input.ref} {input.LR} > {output}) 2> {log}"

rule sam_to_bamLR:      ### compressed to BAM 
    input:
        "data/aligned_read/long_reads/sam_file/"+sample_name+"_LR.sam"
    output:
        "data/aligned_read/long_reads/bam_file/"+sample_name+"_LR.bam"
    threads : 10
    shell:
        "samtools view -@ {threads} -Sb {input} > {output}"

rule sort_bamLR:        ### sort the bam
    input:
        "data/aligned_read/long_reads/bam_file/"+sample_name+"_LR.bam"
    output:
        "data/aligned_read/long_reads/sort_bam/"+sample_name+"_LR_SORTED.bam"
    log:
        "log/samtools_sort/"+sample_name+"LR.log"
    threads:10 
    shell:
        "(samtools sort -@ {threads} {input} -o {output}) 2> {log}"

rule index_bam:        ### indexing the bam file 
    input:
        "data/aligned_read/long_reads/sort_bam/"+sample_name+"_LR_SORTED.bam"
    output:
        "data/aligned_read/long_reads/sort_bam/"+sample_name+"_LR_SORTED.bam.bai"
    shell:
        "samtools index {input}"

################################################## Getting the Two Haplotypes ######################################################################################

rule what_phase:        ### reconstruct the haplotypes
    input:
        ref=expand("data/genome/{genome}.fasta", genome=config["genome"]),
        vcf="data/variant-called/ShortReads/"+sample_name+"SR.vcf",
        LR="data/aligned_read/long_reads/sort_bam/"+sample_name+"_LR_SORTED.bam",
        Index="data/aligned_read/long_reads/sort_bam/"+sample_name+"_LR_SORTED.bam.bai"
    output:
        "data/variant-called/ShortReads/"+sample_name+"_phased.vcf"
    log:
        "log/whatshapp"+sample_name+".log"
    params:
        "--indels"  # phase indels by adding the option
    shell:
        "(whatshap phase --reference {input.ref} --ignore-read-groups -o {output} {input.vcf} {input.LR}) 2>{log}"

rule bgzip:     ##compressing the phased vcf
    input:
        "data/variant-called/ShortReads/"+sample_name+"_phased.vcf"
    output:
        "data/variant-called/ShortReads/"+sample_name+"_phased.vcf.gz"
    shell:
        "bgzip {input}"

rule tabix:     ##indexing the phased compressed vcf
    input:
        "data/variant-called/ShortReads/"+sample_name+"_phased.vcf.gz"
    output:
        "data/variant-called/ShortReads/"+sample_name+"_phased.vcf.gz.tbi"
    shell:
        "tabix {input}"

rule haplo_fasta:       ###Creating phased haplotype in FASTA format
    input:
        vgz="data/variant-called/ShortReads/"+sample_name+"_phased.vcf.gz",
        ref=expand("data/genome/{genome}.fasta", genome=config["genome"]),
        index= "data/variant-called/ShortReads/"+sample_name+"_phased.vcf.gz.tbi"   #just for doing it after tabix
    output:
        h1="result/haplotype/fasta/"+sample_name+"haplotype_1.fasta",
        h2="result/haplotype/fasta/"+sample_name+"haplotype_2.fasta"
    log:
        "log/bcftools/"+sample_name+".log"
    shell:
        "(bcftools consensus -H 1pIu -f {input.ref} {input.vgz} > {output.h1}"
        "&& bcftools consensus -H 2pIu -f {input.ref} {input.vgz} > {output.h2} ) 2> {log}"

#rule are_diff:
#    input:
#        h1="result/haplotype/fasta/"+sample_name+"haplotype_1.fasta",
#        h2="result/haplotype/fasta/"+sample_name+"haplotype_2.fasta"
#    output:
#        txt="result/haplotype/fasta/AreTheHaploDiff.txt"
#    shell:
#        "diff -q {input.h1} {input.h2} > {output.txt}"

rule merge_haplo:   ###Merging the haplotype  
    input:
        h1="result/haplotype/fasta/"+sample_name+"haplotype_1.fasta",
        h2="result/haplotype/fasta/"+sample_name+"haplotype_2.fasta"
    output:
        "result/haplotype/fasta/"+sample_name+"haplotype_merged.fasta"
    shell:
        "cat {input.h1} {input.h2} > {output}"

rule sort_haplo:    ### to having a better plot 
    input:
        "result/haplotype/fasta/"+sample_name+"haplotype_merged.fasta"
    output:
        "result/haplotype/fasta/"+sample_name+"haplotype_sorted.fasta"
    script:
        "script/classiFasta.py"

rule split_chrom: 
    input:
        haplo="result/haplotype/fasta/"+sample_name+"haplotype_sorted.fasta",
        ref=expand("data/genome/{genome}.fasta", genome=config["genome"])
    output:
        directory("result/haplotype/fasta/chromosomes/")
    params:
        '{F=sprintf("result/haplotype/fasta/chromosomes/%s.fasta",$2); print > F;next;} {print >> F;}'
    shell:
        "awk -F '|' '/^>/ {params}' < {input.haplo} "       ###replace '|' by '>' 
        " && awk -F '|' '/^>/ {params}' < {input.ref} "

    
rule nucmer:        ###aligned the haplotype with the reference nucmer 
    input:
        ref=expand("data/genome/{genome}.fasta", genome=config["genome"]),
        fa="result/haplotype/fasta/"+sample_name+"haplotype_sorted.fasta"
    output:
        name="result/delta_file/"+sample_name+".delta"
    log:
        "log/nucmer/"+sample_name+".log"
    shell: 
        "(nucmer --maxmatch --prefix=result/delta_file/{sample_name} {input.ref} {input.fa}) 2> {log}"

rule delta_filter:
    input:
        "result/delta_file/"+sample_name+".delta"
    output:
        "result/delta_file/"+sample_name+"_filtered.delta"
    log:
        "log/delta-filter"+sample_name+".log"
    shell:
        "(delta-filter -m {input} > {output} ) 2> {log}"

rule memmer_plot:
    input:
        "result/delta_file/"+sample_name+"_filtered.delta"
    output:
        gp="result/plots/"+sample_name+".gp"
    log:
        "log/memerplot/"+sample_name+".log"
    shell:
        "(mummerplot -p result/plots/{sample_name} --color -t postscript {input}) 2> {log}"

rule mummer_chrom:
    input:
        directory("result/haplotype/fasta/chromosomes/")
    output:
        directory("result/haplotype/fasta/chrom_align/")
    script:
        "script/alignChrom.py"

rule haplo1_GC:
    input:
        h1="result/haplotype/fasta/"+sample_name+"haplotype_1.fasta"

    output:
        h1="result/haplotype/fasta/"+sample_name+"haplotype_1_gc_content.csv"
    script:
        "script/get_gc.py"       

rule haplo2_GC:
    input:
        h2="result/haplotype/fasta/"+sample_name+"haplotype_2.fasta"
    output:
        h2="result/haplotype/fasta/"+sample_name+"haplotype_2_gc_content.csv"
    script:
        "script/get_gc.py"


################################################## When you finish or need to do it with another data set  ######################################################################################
rule clean :
    input:
        SR=expand("data/short_reads/{short}"+SR_ext , short=config["short_reads"]),
        LR=expand("data/long_reads/{long}"+LR_ext, long=config["long_reads"]),
        fa=expand("data/genome/{genome}.fasta", genome=config["genome"])
    shell:
        "snakemake all --delete-all-output"
        "&& rm {input.SR} {input.LR} {input.fa}"
        "&& rm quality_control/long_reads/* quality_control/short_reads/* data/variant-called/ShortReads/plot/* data/aligned_read/short_reads/readyToCall/* "
        "&& rm -r log/*"
