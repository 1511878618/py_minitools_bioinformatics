#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from functools import reduce
from optparse import OptionParser

import pandas as pd


def matchEncodeID(string):
    return re.search(r"[\w]+[\d]+[\w]+",string).group()

def mkdirs(path):
    try:
        os.makedirs(path)
    except:
        pass

def load_tsvs(path, fields=None):
    if not isinstance(path, (list, tuple)):
        tsv = pd.read_csv(path, sep = "\t")
        tsv.index.name = matchEncodeID(path)
        if not fields:
            return tsv
        if fields:
            return tsv[fields]
    if isinstance(path, (list, tuple)):   
        return [load_tsvs(p, fields) for p in path]
    

def load_RSEM_tsvs(path="./", fields=["expected_count", "TPM", "FPKM"]):
    """
    返回一个[df1, df2]
    """
    keys = ["gene_id", "transcript_id(s)"]
    colnames = keys + fields
    
    RSEM_tsvpath = [os.path.join(path, i) for i in os.listdir(path) if ".tsv" in i and "meta" not in i]
    
    RSEM_tsvsList = load_tsvs(RSEM_tsvpath, colnames)
    return RSEM_tsvsList

def RSEM2matrix(path="./", output="./"):
    fields = ["expected_count", "TPM", "FPKM"]
    keys = ["gene_id", "transcript_id(s)"]
    
    mkdirs(output)
    
    rsem_tsvList = load_RSEM_tsvs(path, fields)
    tsvNames = [i.index.name for i in rsem_tsvList]
    
    # merge两个表以geneid盒transcript_id
    def merge(left, right):
        return pd.merge(left, right, on=["gene_id","transcript_id(s)"], how = "outer")
    
    outputPath = [os.path.join(output, flag+".csv") for flag in fields]

    for flag, output_tsv_path in zip(fields, outputPath):
        flag_tsvList = [i[keys + [flag]] for i in rsem_tsvList]
        flag_csv = reduce(lambda left, right: merge(left, right), flag_tsvList)
        flag_csv.columns = keys + tsvNames
        flag_csv.to_csv(output_tsv_path, index = None)
        
    
        
    
def main():
    usage = 'usage: %prog [options] <RSEM_tev_file_path> <out_path>'
    parser = OptionParser(usage)
    parser.add_option('-i', "--input", default = "./", dest = "inputPath", help="输入RSEM tsv文件所在目录")
    parser.add_option("-o", "--search", default = "./", dest = "output", help="指定输出文件目录")



    (options, args) = parser.parse_args()
    RSEM2matrix(options.inputPath, options.output)

if __name__ == "__main__":
    main()
