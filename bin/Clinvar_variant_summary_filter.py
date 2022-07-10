import pandas as pd 
from optparse import OptionParser

# 忽略部分没有影响的警告
import warnings
warnings.filterwarnings("ignore")
# ------------------------------

def choose_benignOrPathogenic(x):
    x = str.lower(x)
    
    if "benign" == x or "pathogenic" == x or "likely benign" == x or "likely pathogenic" == x:
        return True
    else:
        return False

def ReviewStatus2star(x):
    """标准参见：https://www.ncbi.nlm.nih.gov/clinvar/docs/review_status/"""

    if x =="practice guideline":
        return 4
    if x =="reviewed by expert panel":
        return 3
    if x =="criteria provided, multiple submitters, no conflicts":
        return 2
    if x == "criteria provided, conflicting interpretations" or x == "criteria provided, single submitter":
        return 1
    if x == "no assertion criteria provided" or x == "no assertion provided" or x == "no interpretation for the single variant":
        return 0

def parase_variant_summary_data(inputPath, outputPath, star=2):
    """
    star给与标准参见：https://www.ncbi.nlm.nih.gov/clinvar/docs/review_status/

    根据star过滤variant_summary数据：1. 选择参考基因组为GRch38的nsSNP；2.选择SNV，过滤掉其余类型的变异；3.选择AAS的SNP，这部分Snp Name中会带有P.VAL336GLU这样的内容；4. 根据ReviewStatus给与star，然后根据star过滤；5.输出ClinicalSignificance 是(Likely) Benign 或者 (Likely) Pathogenic的数据
    - param:
        - inputPath: variant_summary.txt  数据下载链接:https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/
        - outputPath: 过滤后的文件目录
    """

    data = pd.read_csv("variant_summary_2022-06.txt", sep="\t")

    if "#" == data.columns[0][0]:  # 如果开头的第一个列名带有# 注释符，去掉它。
        data.rename(columns={data.columns[0]:data.columns[0][1:]}, inplace=True)


    data_GRCh38 = data[data["Assembly"] == "GRCh38"]  # 选择参考基因组为GRch38的nsSNP
    data_GRCh38_SNV = data_GRCh38[data_GRCh38["Type"] == "single nucleotide variant"]  # 选择SNV，过滤掉其余类型的变异
    data_GRCh38_nsSNV = data_GRCh38_SNV[data_GRCh38_SNV["Name"].apply(lambda x : "p." in x)]  # 选择AAS的SNP，这部分Snp Name中会带有P.VAL336GLU这样的内容
    data_GRCh38_nsSNV["star"] = data_GRCh38_nsSNV["ReviewStatus"].apply(ReviewStatus2star)  # 根据ReviewStatus给与star

    data_GRCh38_nsSNV_star = data_GRCh38_nsSNV[data_GRCh38_nsSNV["star"] >=star ]  # 根据star过滤
            
    data_GRCh38_nsSNV_star_binignOrPathogenic = data_GRCh38_nsSNV_star[data_GRCh38_nsSNV_star["ClinicalSignificance"].apply(choose_benignOrPathogenic)]  # ClinicalSignificance 是(Likely) Benign 或者 (Likely) Pathogenic的数据

    data_GRCh38_nsSNV_star_binignOrPathogenic.reset_index(drop=True)  # 重新设立index
    data_GRCh38_nsSNV_star_binignOrPathogenic.to_csv(outputPath,index=0)
    return data_GRCh38_nsSNV_star_binignOrPathogenic

if __name__ == '__main__':
    usage = "usage: %prog [options] <input_filePath>[output_filePath]\nstar给与标准参见：https://www.ncbi.nlm.nih.gov/clinvar/docs/review_status/。流程如下：\n1. 选择参考基因组为GRch38的nsSNP；\n2.选择SNV，过滤掉其余类型的变异；\n3.选择AAS的SNP，这部分Snp Name中会带有P.VAL336GLU这样的内容；\n4. 根据ReviewStatus给与star，然后根据star过滤；\n5.输出ClinicalSignificance 是(Likely) Benign 或者 (Likely) Pathogenic的数据"
    parser = OptionParser(usage, )
    parser.add_option("-i", "--input", dest = "input_filePath", default="variant_summary_2022-06.txt", help="请输入variant_summary文件")
    parser.add_option("-o", "--output", dest = "output_filePath", default="variant_summary_star2_filter.csv", help="指定输出文件")
    parser.add_option("-s", "--star", dest="star", default=2, type="int", help="输出大于等于star的数据")
    (options, args) = parser.parse_args()

    parase_variant_summary_data(options.input_filePath, options.output_filePath, star=options.star)