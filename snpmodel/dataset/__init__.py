import re
import sys
from collections import Counter

import pandas as pd
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchtext.vocab import vocab


from .nsSNP_seq_data import get_clinvar_dataset_seq  # 导入nsSNP数据

amino_acid_alphabet={"Ala":"A", "Phe":"F", "Cys":"C", "Sec":"U", "Asp":"D", "Asn":"N", "Glu":"E", "Gln":"Q", "Gly":"G", "His":"H", "Leu":"L", "Ile":"I", "Lys":"K", "Pyl":"O", "Met":"M", "Pro":"P", "Arg":"R", "Ser":"S", "Thr":"T", "Val":"V", "Trp":"W", "Tyr":"Y"}

amino_acid_alphabet1to3 = {v:k for k, v in amino_acid_alphabet.items()}
