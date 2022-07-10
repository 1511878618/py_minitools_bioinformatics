#!/usr/bin/env python3

import json
import os
import threading
import time
from itertools import chain
from optparse import OptionParser

import httplib2
import pandas as pd


def download_ChrRange(chr="chr1", start=69000, end=70000, as_dataframe=False, GeneSymbol="unknown", **kwargs):
    """
    download_ChrRange 从https://myvariant.info/v1/api#/整合数据库中获取指定基因组区域内所有SNP

    Args:
        chr (str, optional): 输入染色体号. Defaults to "chr1". e.g. chr1 chrX chrY ...
        start (int, optional): 区域的起始位置. Defaults to 69000.
        end (int, optional): 区域的终止位置. Defaults to 70000.
         
        as_dataframe (bool, optional): 是否输出dataframe. Defaults to False.
        GeneSymbol: GeneSymbol
        kwargs: fetch_all=True 下载所有的数据; email: email (str, None): 邮箱地址，以免不小心被myvariant数据库当爬虫杀掉。。 ; fields 指定过滤的fields;参见https://docs.myvariant.info/en/latest/doc/data.html#data-sources
    Returns:
        _type_: list or dataframe
    """

    # 构建http请求
    h = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    # 初始化参数
    hits = []  # 检索到的snp存放
    scroll_id = None  # 继续请求后续的SNP的key， see more:https://docs.myvariant.info/en/latest/doc/variant_query_service.html#query-syntax
    gotsnps = 0  # 已经获取到的Snp个数，如果小于检索回来的total则说明该区域的snp数量超过1000个，而超过1000个则需要使用scroll_id来继续请求，这样的机制是反爬虫的一种~。。。。
    total = 1  #随便一个初始值保证循环开始即可

    while gotsnps < total:  # 确保下载完该区域所有的snp 
        params = f"q={chr}:{start}-{end}" 

        params +=''.join([f"&{k}={v}" for k,v in kwargs.items()])  # 添加额外的query内容

        if scroll_id:
            params += f"&scroll_id={scroll_id}" 
        else:
            pass 

        res, con = h.request('http://myvariant.info/v1/query', 'GET', params, headers=headers)
        con = json.loads(con)
        hits.append(con["hits"])  # 添加下载到的数据到列表中保存

        total = con["total"]  # 更新total
        gotsnps += len(con["hits"])  # 更新计数

        if total == 0:  #如果这个区域没有则终止循环
            break 

        try:  #如果不是fetch_all则没有它
            scroll_id = con["_scroll_id"]  # 更新scroll_id
        except:  #则下载完了可以结束
            break 

    print(f"finish query from https://myvariant.info/v1/api#/ \n got {total} snp at this genomic location:{GeneSymbol} and already download {gotsnps}\n")

    hits = list(chain(*hits))  # 一定要加上list，否则会少一行？一个chain的bug?

    if as_dataframe:  # 输出df
        return pd.json_normalize(hits)
    else:
        return hits


def downloadAndSaveByBed(data, save_path, **kwargs):
    """
    downloadAndSaveByBed 通过myvariant数据库，根据Bed文件下载对应的区域内所有的SNP数据

    Args:
        data (dataframe): bed的数据，读入后
        save_path (str): 保存目录，按bed文件第四列命名
        kwargs: fetch_all=True 下载所有的数据; email: email (str, None): 邮箱地址，以免不小心被myvariant数据库当爬虫杀掉。。 ; fields 指定过滤的fields;参见https://docs.myvariant.info/en/latest/doc/data.html#data-sources
    """
    try:    
        os.mkdir(save_path)
    except:
        pass

    error = []
    print(f"文件下载保存在:{save_path}")
    for idx, values in data.iterrows():
        genename = values["GeneSymbol"]
        try:
            output = f"{save_path}/{genename}.csv"
            out = download_ChrRange(as_dataframe=True,fetch_all=True, **values.to_dict(), **kwargs)  # 获取染色体号、起始位置、终止位置作为输入
            out.to_csv(output, index=None)
        except:
            error.append(genename)
            print(f"{genename} is wrong")
        time.sleep(3)


def downloadByThread(dataframe, threads_num=10, save_path="./associateGeneRangeSNP",*args, **kwargs):

    """
    downloadByThread 多线程的对myvariant数据库进行请求下载，输入bed文件格式的dataframe

    Args:
        dataframe (_type_): bed file
        email (_type_): email 
        threads_num (int, optional): threads num . Defaults to 10.
        save_path (str, optional): output path. Defaults to "./associateGeneRangeSNP".
    """

    try:    
        os.mkdir(save_path)
    except:
        pass

    length = dataframe.shape[0]
    steps = length // threads_num 
    threads = []
    for idx, i in enumerate(range(0, length, steps)):
        
        tmp_data = dataframe.iloc[i:i+steps, :]
        thread = threading.Thread(
        target=downloadAndSaveByBed, 
        args=(tmp_data, save_path),
        kwargs=kwargs
        )
        threads.append(thread)
    
    for thread in threads:
        thread.start()

if __name__ == '__main__':
    usage = "usage: %prog <bed> <output> <threads num> <email>"

    parser = OptionParser(usage, )
    parser.add_option("-i", "--input", dest = "bed_file_path", default="Clinvar_SNP_Gene_full.bed", help="请输入要下载的包含感兴趣的基因组片段的bed文件")
    parser.add_option("-o", "--output", dest = "dir", default="associateGeneRangeSNP", help="指定输出保存目录，按bed文件第四列进行排列")
    parser.add_option("-t", "--threads_num", dest="threads_num", default=10, type="int", help="使用的线程个数")
    parser.add_option("-m", "--email", dest="email", default=None, type="str", help="指定邮箱")
    (options, args) = parser.parse_args()

    email = options.email
    bed = pd.read_csv(options.bed_file_path, names=["chr", "start", "end", "GeneSymbol"], sep="\t")
    dir = options.dir  # 保存目录 
    print(f"saveing file to {dir}, please check")
    downloadByThread(bed, threads_num=options.threads_num, save_path=dir, email="xutingfeng@big.ac.cn")
    print(f"finish downloading.......")
