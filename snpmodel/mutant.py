from . import *
from .dataset import amino_acid_alphabet, amino_acid_alphabet1to3
from .dataset.preprocess import padding_fixLengthSeq
import re 
from .utils import * 


def all_possible_mutant(protein_seq):
    out = []
    for origin, pos in zip(protein_seq, range(len(protein_seq))):
        pos_possible = []
        pos_3alphabet = amino_acid_alphabet1to3[origin]
        
        for pos_mutant, v in amino_acid_alphabet.items():
            pos_possible.append(f"{pos_3alphabet}{pos}{pos_mutant}")
        out.append(pos_possible)
    return out

def split_AAS(AAS):
    """
    AAS: like Val0Ala
    """
    
    AAS_list = re.split(r"([0-9]+)", AAS)
    origin = AAS_list[0] if AAS_list[0] else None  
    pos = int(AAS_list[1]) - 1 if AAS_list[1] else None
    mutant = AAS_list[2] if AAS_list[2] else None
    
    return origin, pos, mutant



def all_possible_mutant_sequence(protein_seq, fix_length = None, padding="<pad>"):
    """
    输入蛋白序列，获得所有突变的序列情况（AAS）， fix_length和padding必须一起使用，fix_length 应当输入2的倍数
    
    Return 
        list， 每一个突变序列均是list保存，返回是所有突变序列的list对象的集合
    """
    all_possible_mutant_hgvs = all_possible_mutant(protein_seq)
    out = []
    hgvs_label = []
    for pos_hgvs in all_possible_mutant_hgvs:  # 按每个位置进行迭代，
        for hgvs in pos_hgvs:
            origin, pos, mutant = split_AAS(hgvs)
            mutant_seq = list(changeStrByPos(protein_seq, pos, amino_acid_alphabet[mutant]))  # 转化成list类型

            if fix_length and padding:
                mutant_seq = padding_fixLengthSeq(mutant_seq, pos, fix_length, padding)  # 按指定长度进行截取

            out.append(mutant_seq)
            hgvs_label.append(hgvs)
        
    return out, hgvs_label
