import numpy as np
from Bio import Medline
from Bio import Entrez #Entrez查询
from collections import Counter
from wordcloud import WordCloud #词云
import matplotlib.pyplot as plt #显示图像
from functools import reduce
from optparse import OptionParser


class pubmed_wordcloud:
    def __init__(self,mail,):
        self.mail = mail
        self.Entrez = Entrez
        self.Entrez.email = mail

    def search(self, term, retmax = 1000):
        results = self.Entrez.esearch(db="pubmed",
                            term = term,
                            retmax = retmax)
        id_list = self.Entrez.read(results).get("IdList","?")
        if id_list == "?":
            print("没有搜索到结果")
            return None
        else:
            print(f"检索到:{len(id_list)}相关文献")
            results = self.Entrez.efetch(db = "pubmed", 
                                         id=id_list, 
                                         rettype="medline",
                                         retmode="text")
            self.records =list(Medline.parse(results))
            
            titles = [record.get('TI','?') for record in self.records]
            self.titles_text = reduce(lambda a,b: a+b,titles )
            
            abstracts = [record.get('AB','?') for record in self.records]
            self.abs = reduce(lambda a, b: a+b, abstracts)
            
    def generate_wordcloud(self,use = "title",**kw):
        """可以使用的额外参数有:
              use = "abs" or "titles"
              scale=20,
              background_color="black",
              figsize=(10, 20),
              dpi=200
        """
        params = {"scale":20,
                  "background_color":"black",
                  "figsize":(10, 20),
                  "dpi":200
                  }
        params.update(kw)
            
        if use == "title":
            texts = self.titles_text
        if use == "ab" or "abstract":
            texts = self.abs
        else:
            print("输入正确的用于制作词云的类型，eg: use = 'ab'")
            
        self.wordcloud = WordCloud(scale=params["scale"],background_color=params["background_color"]).generate(texts)
        plt.figure(figsize=params["figsize"],dpi=params["dpi"])
        plt.title(f"Use: {use}")
        plt.imshow(self.wordcloud, interpolation='bilinear')
        
    
    def save(self,filePath):
        print(f"保存到:{filePath}")
        self.wordcloud.to_file(f"{filePath}.png")
    def save_searchResults_to_file(self, file_name):
        if isinstance(self.records,list):
            with open(f"{file_name}.txt","w") as f:    
                for record in self.records:
                    title = record.get("TI","?")
                    ab = record.get("AB","?")
                    f.write(f"{title}\n{ab}\n\n")



def main():

    usage = 'usage: %prog [options] <genome_hic_file> <seqs_bed_file> <seqs_hic_file>'
    parser = OptionParser(usage)
    parser.add_option('-m', "--mail", dest = "mail", help="输入你的NCBI账户，eg:xxx@xxx")
    parser.add_option("-s", "--search", dest = "term", help="输入你要在pubmed上搜索的内容，并用于制作词云")
    parser.add_option("-n", "--max_num", type = "int", default = 1000, dest = "retmax", help = "用于词云最大的文献数量")
    # parser.add_option("-S", "--scale", type = "int", default=20, dest = "scale", help="词云的精度")
    parser.add_option("-o", "--output", dest = "fileName")


    (options, args) = parser.parse_args()

    kw = {"scale":20, "figsize":(10,10)}
    pw = pubmed_wordcloud(mail=options.mail)
    pw.search(term=options.term, retmax=options.retmax)
    pw.save_searchResults_to_file(options.fileName)
    pw.generate_wordcloud(use="title", **kw)
    pw.save(f"{options.fileName}_title")

    pw.generate_wordcloud(use="abs", **kw)
    pw.save(f"{options.fileName}_abstract")

if __name__ == "__main__":
    main()
        