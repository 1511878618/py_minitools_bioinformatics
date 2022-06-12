#!/usr/bin/env python
# coding: utf-8

# In[40]:


import os 
from Bio import SeqIO
from collections import Counter

# 读取基因组文件，并返回基因组长度和基因组序列
def len_genome_SEQ():
    path = "./exemple/"
    filename = os.listdir(path)
    for file in filename:
        position = path + "/" + file
        SEQ = []
        len_genome = []
        for seq_record in SeqIO.parse(position,"fasta"):
            seq_seq = str(seq_record.seq)
            SEQ.append(seq_seq)
            seq_len = len(seq_seq)
            len_genome.append(seq_len)
    #         seq_len = len(str(seq_record.seq))
    #         len_genome.append(seq_len)
    return len_genome,SEQ

def sliding_kmer(kmer,sliding_window):
    #kmer_listall = [] #所有基因组的列表联合
    kmer_list = [] #单一基因组的kmer列表
    
    genome_length,seq = len_genome_SEQ()
    #由于得到的genome_length和seq都是列表，for循环取出其中的序列信息
    for j in range(0,len(seq)):
        genome_len = genome_length[j]
        sequence = seq[j]
    #添加kmer和滑窗
        for i in range(0,genome_len,sliding_window):
            I_window = sequence[i:i+kmer]
            kmer_list.append(I_window)
        # kmer_listall.append(kmer_list)
            
#             #将每个kmer的集合计算交集
#             for k in range(0,len(kmer_listall)):
#                 k_set = set(k)
            if len(I_window) < kmer:
                break
    print(kmer_list)
    print(genome_length,seq)

#将所有得到的kmer放到一个大列表中，计算每一个kmer在不同基因组中出现的次数
kmer_list_all = kmer_list.extend(#所有的list)


def main():
    sliding_kmer(100,10)
    
main()


# In[37]:


import os 
from Bio import SeqIO
from collections import Counter

# 读取基因组文件，并返回基因组长度和基因组序列
def len_genome_SEQ():
    path = "./exemple/"
    filename = os.listdir(path)
    for file in filename:
        position = path + "/" + file
        SEQ = []
        len_genome = []
        for seq_record in SeqIO.parse(position,"fasta"):
            seq_seq = str(seq_record.seq)
            SEQ.append(seq_seq)
            seq_len = len(seq_seq)
            len_genome.append(seq_len)
    #         seq_len = len(str(seq_record.seq))
    #         len_genome.append(seq_len)
    return len_genome,SEQ
    print(seq_seq)
len_genome_SEQ()


# In[ ]:





# In[ ]:




