from . import *
from .preprocess import build_vocab, SNP_flaking_fixLengthSeq
def load_data(Clinvar_seq_data_path="Clinvar_seq_data.csv", remove_ter = False):
    try:
        data = pd.read_csv(Clinvar_seq_data_path, sep = "\t")
    except FileNotFoundError:
        print("请指定正确的文件位置")

    # print(data.columns)
    if remove_ter:
        data = data[data["p.HGVS"].apply(lambda x: "Ter" not in x)]
        
    return [data[col].tolist() for col in data.columns]

def clinvar_dataset(path = "Clinvar_seq_data.csv", remove_ter=True):
    """
    读入的文件包含前五列：p.HGVS, GeneSymbol, label, ref_seq, mutant_seq
    
    Return:
        list, vocab
    """
    name, GeneSymbol, label, ref_seq, mutant_seq= load_data(path, remove_ter=remove_ter)
    aa_vocab = build_vocab(ref_seq)
    aa_vocab.vocab.set_default_index(0)  # 设定默认
    vocab_length = len(aa_vocab.get_itos())
    ref_seq, mutant_seq = SNP_flaking_fixLengthSeq(name, ref_seq, mutant_seq, length=100)

    out = []
    for n, l, m in zip(name, label, mutant_seq):
        m_tensor = torch.tensor(aa_vocab.vocab.lookup_indices(m))
        m_tensor = F.one_hot(m_tensor, vocab_length)
        m_tensor = m_tensor.float()
        
        l = 1 if "pathogenic" in l.lower() else 0
        l_tensor = torch.tensor(l, dtype = torch.long)
        l_tensor = F.one_hot(l_tensor, 2)
        out.append([n, m_tensor, l_tensor])
        
    return out, aa_vocab


def get_clinvar_dataset_seq(path = "Clinvar_seq_data.csv"):
    """
    读入的文件包含前五列：p.HGVS, GeneSymbol, label, ref_seq, mutant_seq
    Return:
        3个数据集
    """
    out, aa_vocab = clinvar_dataset(path)
    # total = DataLoader(out, batch_size=512, shuffle=True)
    length = len(out)
    
    train_size, validate_size=int(0.7 * length), int(0.1 * length)
    test_size = length - train_size - validate_size
    print(f"train_data size: {train_size} + validate_data size: {validate_size} + test_data size:{test_size} = {length}")
    
    train_set, validate_set, test_set = random_split(out, [train_size, validate_size, test_size], generator=torch.Generator().manual_seed(42))
    
    return (DataLoader(train_set, batch_size=512, shuffle=True), DataLoader(validate_set, batch_size=512, shuffle=True), DataLoader(test_set, batch_size=512, shuffle=True)), aa_vocab
