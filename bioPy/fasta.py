import os 
import Bio
from collections import Counter
import re
from itertools import chain
from functools import reduce
import pandas as pd

def kmer(seq:Bio.SeqRecord.SeqRecord, k:int=20, stride:int=2):
    """
    用于切分kmer序列，

    Parameters:
      seq: SeqRecord类型或者str
      k - kmer大小
      stride - 步长

    Returns:
        list,[kmer_1, kmer_2,..., kmer_n]

    Raises:
        KeyError - raises an exception
    """
    
    if isinstance(seq, Bio.SeqRecord.SeqRecord):
        seq = seq.seq
    elif isinstance(seq, str):
        seq = seq 
    else:
        print("传入Seqrecord或者str类型")
        raise TypeError
        
    length = len(seq)
    
    return [str(seq[i: i + k]) for i in range(0, length, stride) if i + k <= length ]
        
        
def readFastaFileFromGivenPath(path):
    """
    Return:
        一个包含所有fasta序列的迭代器
    """
    pathList = [os.path.join(path, file) for file in os.listdir(path) if re.match(f".+fasta", file) ]
    fastaIterList = [Bio.SeqIO.parse(fastaPath, "fasta") for fastaPath in pathList]
    return chain(*fastaIterList)


def genomes2kmer(path, output = "./htt.csv", k = 20, stride = 10):
    """
    用去切分基因组序列成kmer片段，按照stride进行切割。
    切分：[genome[i:i+k] for i in range(i, genomeLength, stride)]
    最后返回的是一个csv文件，第一列是kmer序列，剩余列是各个基因组中该kmer的频次
    
    Parameters:
      path - 指定基因组序列存储的位置，该目录下可以有多个.fasta文件
      output - 输出目录
      k - kmer大小
      stride - 步长

    Returns:
        csv file

    """
    CounterList = []
    genomeIdList = []
    for fasta in readFastaFileFromGivenPath(path):
        genomeIdList.append(fasta.id)
        kmerSeq = kmer(fasta, k, stride)
        CounterList.append(Counter(kmerSeq))
    
    allKmerCounter = dict(reduce(lambda x, y : x + y, CounterList))
    
    result = []
    for key in allKmerCounter.keys():
        distribution = [genomedic.get(key, 0) for genomedic in CounterList]

        result.append(pd.DataFrame([[key, *distribution]], columns=[f"{k}-mer", *genomeIdList]))   
    
    result = pd.concat(result)
    result.to_csv(output,index=0)
    return result
        
        