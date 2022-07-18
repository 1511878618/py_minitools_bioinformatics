from . import *

def build_vocab(seq_list):
    """
    build_vocab [list, list]

    Args:
        seq_list (list): 包含多个分词好了的序列的迭代器

    Returns:
        vocab: torchtext.vocab类型
    """
    couter = Counter()
    for seq in seq_list:
        for aa in seq:
            couter.update(aa)
    return vocab(couter, specials = ['<unk>', '<pad>'])



def splitAAS_HGVS(AAS):
    """
    splitAAS_HGVS p.VAL321ILE 格式的蛋白质序列的HGVS命名

    Args:
        AAS (str): HGVS命名

    Returns:
        origin, pos, mutant: 返回一个包含ref, pos ,mutant的tuple
    """
   
    AAS = re.search(r"(?<=p.).*", AAS).group()
    AAS_list = re.split(r"([0-9]+)", AAS)
    ref = AAS_list[0] if AAS_list[0] else None  
    pos = int(AAS_list[1]) - 1 if AAS_list[1] else None
    mutant = AAS_list[2] if AAS_list[2] else None
    return ref, pos, mutant


def padding_fixLengthSeq(seq, pos, length, padding="<pad>"):
    """
    padding_fixLengthSeq 给定序列，指定选取的位置，从这个位置左右取2/length的子序列

    Args:
        seq (str): 给定序列
        pos (int): 中心位置
        length (int): 取的长度，偶数
        padding (str, optional): 填充的字符. Defaults to "<pad>".

    Returns:
        list: list中一个位置为一个最小的token
    """



    assert length%2 == 0, "请输入偶数，以保证左右取到的子序列是相同长度的。"
    
    if isinstance(seq ,list):
        pass
    else :
        seq = list(seq)
    left_seq = seq[:pos]
    right_seq = seq[pos+1:]
    half_length = length//2
    left_padding = [padding]*(half_length - len(left_seq)) if len(left_seq) < half_length else []
    left_seq = left_padding + left_seq
    
    right_padding = [padding]*(half_length - len(right_seq)) if len(right_seq) < half_length else []
    right_seq = right_seq + right_padding
    
    return left_seq[-half_length:] + [seq[pos]] + right_seq[:half_length] 


def SNP_flaking_fixLengthSeq(HGVS_list:list, ref_seq_list:list, mutant_seq_list:list, length = 40, padding='<pad>'):
    """
    SNP_flaking_fixLengthSeq 给定HGVS和对应的ref序列和突变序列，切分获得子序列

    Args:
        HGVS_list (list): HGVS
        ref_seq_list (list): 参考序列list
        mutant_seq_list (list): 突变序列list
        length (int, optional): 子序列的长度. Defaults to 40.
        padding (str, optional): 填充字符. Defaults to '<pad>'.

    Returns:
        tuple: (fix_ref_seq, fix_mutant_seq)
    """

    fix_ref_seq = []
    fix_mutant_seq = []
    for hgvs, ref_seq, mutant_seq in zip(HGVS_list, ref_seq_list, mutant_seq_list):
        ref_seq, mutant_seq = list(ref_seq), list(mutant_seq)
        orgin, pos, mutant = splitAAS_HGVS(hgvs)
        fix_ref_seq.append(padding_fixLengthSeq(ref_seq, pos, length, padding))
        fix_mutant_seq.append(padding_fixLengthSeq(mutant_seq, pos, length, padding))
        
    return fix_ref_seq, fix_mutant_seq

