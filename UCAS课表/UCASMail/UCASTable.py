
import pandas as pd 

import re 

import numpy as np 
import os
import datetime

### 处理单个课程的数据类

class course(object):
    def __init__(self):
        self.name = None
        self.time = None
        self.classroom = None # a dict
        self.Range = None
        self.week = None
        self.classPerWeek = None
        
    def __str__(self):
        print(name,week,time,classroom,Range)
        
    def getUCASInfo(self,INPUT=True,text=None):
        """
        把UCAS个人课表中的表格内容 作为 text的输入。
        
        该函数提取其中的一些信息，作为course类的属性。
        
        """
        

        if INPUT:
            if text:
                # print('using file as input')
                a = text
            else:
                a = input("输入：")
            
            self.name = re.findall(r'课程名称：[^  ]*',a)[0].split('：')[1]
            self.week = re.findall(r'星期.{1}',a)
            self.time = [list(map(int,i[1:-1].split('、'))) for i in re.findall(r'第[\d、]*节',a)]
            self.Range = [list(map(int,i.split('\t')[1].split('、') )) for i in re.findall(r'上课周次\s[\d、]*',a)]
            self.classroom = re.findall(r'上课地点\s[^ ]*',a)[0].split('\t')[1]
            
            self.classPerWeek = len(self.week)


        else:
            self.name = input("输入课程名：")
            self.classroom = input("输入教室信息（如：一教225）：")
            self.week = input("请输入上课的时间（如：星期一）：")
            self.time = list(map(int,input("输入课程的上课时间点（如：第7、8节）：")[1:-1].split('、')))
            self.Range = list(map(int,input("输入上课的周次（如：13、14、15、16、17）：").split('、')))
            

### 生成TABLE

class Table(object):
    def __init__(self,courses):
        self.courses = courses #传入一个列表，包含所有上的课的course类。
        self.semester= {} #学期开始的周一时间，一学期有多久
        self.semesterTable = None
        
    def generateTable(self):
        
        #生成25周的课程表
        
        semesterTable = [ pd.DataFrame(index=range(1,13),columns=["星期{}".format(i) for i in range(1,8)]) for week in range(1,26)]
        
        for course in self.courses:
            for i in range(course.classPerWeek):
                
                #星期几上课
                if len(course.week) == course.classPerWeek:
                    weekTime = course.week[i]
                else:
                    weekTime = course.week
                    
                # 该天上课的时间段
                if len(course.time) == course.classPerWeek:
                    dayTime = course.time[i]
                else:
                    dayTime = course.time

                weekLasting = course.Range[i]

                courseName = course.name
                
                if len(course.classroom) == course.classPerWeek:
                    classroom = course.classroom[i]
                else:
                    classroom = course.classroom
                    
#                 print(dayTime,weekTime,'\t',type(dayTime[0]),type(weekTime))
                
                for i in weekLasting:
                    weekTable = semesterTable[i-1]
                    weekTable['time'] = ["8:30~9:20","9:20~10:10","10:30~11:20","11:20~12:10","13:30~14:20","14:20~15:10","15:30~16:20","16:20~17:10",
               "18:10~19:00","19:00~19:50","20:10~21:00","21:00~21:50"]
                    weekTable.iloc[dayTime[0]-1:dayTime[-1],turnChineseWeekToNumberWeek(weekTime)-1] = course.name +'({})'.format(classroom)
                    
                    weekTableColumns = weekTable.columns
                    weekTableColumns = weekTableColumns[:-1].insert(0,weekTableColumns[-1])
                    weekTable = weekTable[weekTableColumns]
        self.semesterTable =  semesterTable
        return semesterTable
        
        
def showWeekOfSemester(semesterYear=2022):
    """
    semesterYear是本学期开学的年份
    这个函数用于帮助用户查看学期第一周是本年的第几周。
    1.查询本周是今年的第几周，i周
    2.然后用户自行根据目前是本学期的第几周,a周
    3.可以推算本学期开学是今年的第 i-a+1 周。    
    """
    
    today = datetime.datetime.today()
    todayIsocalendar = today.isocalendar()
    
    i = todayIsocalendar[1]
    
    print("今天的日期是：{}\t今天是今年的第{}个周{} ".format(today,todayIsocalendar[1],todayIsocalendar[2]))
    
    a = eval(input("今天是本学期的第几周？:"))
    
    out = i-a+1 
    weekStart = datetime.date.fromisocalendar(semesterYear,out,1)
    
    
    text = "本学期开学时间是:{}\t 是今年的第几周:{}".format(weekStart,out)
    print(text)
    with open("semester.info",'a') as f:
        f.write(text)
    
    return {"semesterBegin" : weekStart, "semesterBeginWeek" : out}


def turnChineseWeekToNumberWeek(chineseWeek):
    
    dic={"星期一":1,"星期二":2,"星期三":3,"星期四":4,"星期五":5,"星期六":6,"星期日":7}
    return dic[chineseWeek]

def readUCASClassInfoFromFile(file):
    """返回包含有多个课程的信息的一个list"""
    with open(file) as f :
        texts=f.read()
    textIndex = [i.span()[0] for i in re.finditer('课程名称',texts)]#从读入的数据中找到每一个课程的信息 的索引
    textIndex.append(len(texts))#添加上最后一位的索引
    #读取对应的text的信息
    textsList = [texts[textIndex[x]:textIndex[y]] for x,y in zip(range(0,len(textIndex)),range(1,len(textIndex)))]
    #去除每一个text前后的换行符等
    def strip(x):
        return x.strip()
    textsList = list(map(strip,textsList))
    return textsList

#处理课程信息
# def main_Type():
#     usr = input('输入你的名字：')

#     usrTablePath = 'table/'+usr
#     courses = []
#     try:
#         os.makedirs(usrTablePath)
#     except:
#         pass
#     while (True):
#         tmpCourse = course()
#         tmpCourse.getUCASInfo()
#         courses.append(tmpCourse)
#         flag = input("是否继续输入(y/n)")
#         if flag == 'n':
#             break
#     #     print(tmpCourse.classPerWeek)
#     #生成课表
#     classTable = Table(courses)
#     classTableList = classTable.generateTable()
#     [y.to_csv(usrTablePath+"/{}周.csv".format(x+1),index=0) for x,y in zip(range(len(classTableList)),classTableList)]
#     return classTableList



def main(file):
    #处理用户信息，添加到数据库中
    usr = input('输入你的名字：')
    mail = input('输入你的邮箱：')
    try:
        usrData = pd.read_csv('user.csv')
        usrData = usrData.append({'userName': usr,"mailAddress": mail},ignore_index=True)
        usrData = usrData.drop_duplicates()
        usrData.to_csv('user.csv',index=0)
    except:
        usrData = pd.DataFrame({'userName': usr,"mailAddress": mail},index=[0])
        usrData.to_csv('user.csv',index=0)

    usrTablePath = 'table/'+usr
    courses = []
    try:
        os.makedirs(usrTablePath)
    except:
        pass
    textsList = readUCASClassInfoFromFile(file)
    for text in textsList:
#         print(text)
        tmpCourse = course()
        tmpCourse.getUCASInfo(INPUT=True,text=text)
        courses.append(tmpCourse)
    #     print(tmpCourse.classPerWeek)
    #生成课表
    classTable = Table(courses)
    classTableList = classTable.generateTable()
    [y.to_csv(usrTablePath+"/{}周.csv".format(x+1),index=0) for x,y in zip(range(len(classTableList)),classTableList)]
    return classTableList


##使用请
#需要修改这个地方

####这个是确认本学期开学的时间，请在showWeekOfSemester处添加开学年份。
if os.path.exists('semester.info'):
    pass
else:
    showWeekOfSemester()
####over####

##主代码，需要修改输入~~~~~
main("test.txt")