from . import *
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns 
from .dataset import amino_acid_alphabet
from .mutant import all_possible_mutant_sequence
from .model.seq_models import predict


def featureMap_array(seq, model, aa_vocab, name="unk", fix_length=100):
    mutants_seqs, hgvs = all_possible_mutant_sequence(seq, fix_length)
    data = []
    for mutant_seq in mutants_seqs:
        m_tensor = torch.tensor(aa_vocab.vocab.lookup_indices(mutant_seq))
        m_tensor = F.one_hot(m_tensor, len(aa_vocab))
        m_tensor = m_tensor.float()
        data.append(m_tensor)
    dataIter = DataLoader(data, batch_size=512, shuffle=False)
    pred = predict(dataIter, model)
    hgvs = np.array(hgvs)
    return pred, hgvs

### 用于画图
def draw_mutant_heatmap(pred, name="unk", **kwargs):

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300, sharex=False)
    y_data = [pred[:, :, 0], pred[:, :, 1], pred.argmax(-1)]
    for ax, y_, title_ in zip(axes, y_data, ["Benign", "Pathogenic", "Benign or pathogenic"]):
        pic = sns.heatmap(y_, ax = ax, xticklabels= list(amino_acid_alphabet.keys()),**kwargs)
        ax.set_title(f"{name}'s {title_} map")