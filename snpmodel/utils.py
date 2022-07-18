# -*- coding: utf-8 -*-


from . import *


"""
常用的函数集合
    - Accumulator
    - changeStrByPos
"""


class Accumulator:
    """ 在n个变量上累加 """
    def __init__(self, n):
        self.data = [0.0] * n 
    
    def add(self, *args):
        self.data = [a + float(b) for a, b in zip(self.data, args)]
    
    def reset(self):
        self.data = [0.0] * len(self.data)
    def __getitem__(self, idx):
        return self.data[idx]
    

def changeStrByPos(string:str, idx, new):
    """
    更改一个字符串的某个位置的元素
    """
    tmp = list(string)
    tmp[idx] = str(new)
    return ''.join(tmp)
    

def modelParametersNum(model):
    totalNum = sum([i.numel() for i in model.parameters()])
    print(f'模型总参数个数：{sum([i.numel() for i in model.parameters()])}')
    return totalNum
    
def mkdirs(path):
    try:
        os.makedirs(path)
    except:
        pass

def try_gpu():
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda:0"
    return device
