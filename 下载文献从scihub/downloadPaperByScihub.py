#!/usr/bin/env python
# -*-coding:utf-8 -*-

from scihub import SciHub

sh = SciHub()

def downloadPaperFromFile(fileName):
    
    if fileName.endswith('.txt'):
        with open(fileName,'r') as f:
            urls = f.readlines()
        urls =list( map(lambda x: x.strip(),urls))
        for url in urls:
            result = sh.fetch(url)
            name = result['name']
            with open(name+'.pdf','wb') as f:
                f.write(result['pdf'])

def main():
    usage = 'usage: %prog [options] <paper> <seqs_bed_file> <seqs_hic_file>'
       
downloadPaperFromFile('paper.txt')