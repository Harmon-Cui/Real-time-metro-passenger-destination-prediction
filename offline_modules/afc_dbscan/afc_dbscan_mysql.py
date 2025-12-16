#!/usr/bin/python3
import pymysql
from  datetime import datetime
import random
import numpy as np  # 数据结构
import sklearn.cluster as skc  # 密度聚类
import pymysql
import pandas as pd
import numpy as np  # 数据结构
import os
import sys
import time

EPS_SET=15 # 预置的密度半径参数C
DestNameDict = dict()
DestNameDictRev = dict()
def getDestNameCode(dest):
    if dest not in DestNameDict.keys():
        DestNameDict[dest] = (len(DestNameDict)+1) *  EPS_SET + EPS_SET * 2
        DestNameDictRev[DestNameDict[dest]] = dest
    #print(dest + " | " + str(DestNameDict[dest]))
    return DestNameDict[dest]
#获取时间编码
def getTimeCode(b):
    b_change = datetime.strptime(b, "%Y/%m/%d %H:%M:%S")
    timecode = b_change.hour * 60 + b_change.minute;
    return timecode

#获取唯一tickeet_ID集合
def getUniqTicketID(trips):
    ticketId = set()  # 用户数: 1344309
    for trp in trips.values:
        ticketId.add(trp[0])
    return ticketId
###主处理函数
def process(sqlStr, usr, pwd, db):
    print(" 获取源数据...")
    conn1 = pymysql.connect (host='localhost',user='root',password= "chm123" ,db='bjtu',port=3306,charset='utf8')
    conn2 = pymysql.connect(host='localhost', user='root', password="chm123", db='bjtu', port=3306, charset='utf8')
    curs2 = conn2.cursor()
    trpsql = sqlStr
    trips = pd.read_sql(trpsql, conn1)  # 数据量10887109
    # 所有数据都读取到trips里面了，对trips进行操作
    #ticketIdSet = getUniqTicketID(trips) # 获取唯一的ticketID
    uniqueTicketList = list(trips['TICKET_ID'].unique())
    ticketCnt = pd.DataFrame(trips['TICKET_ID'].value_counts())
    pseries = ticketCnt.TICKET_ID
    trips = trips.set_index('TICKET_ID')
    cnt = 0
    n = 0  # 写入数据库循环的参数
    data_sql = [] #待写入数据库的列表
    print("数据预处理完成,当前时间：" + str(time.asctime(time.localtime(time.time()))))
    print("     ID记录数: " + str(len(uniqueTicketList)) )
    print("     出行记录数: " + str(len(trips)) )
    print("开始聚类: " + str(time.asctime(time.localtime(time.time()))) )
    for psg in uniqueTicketList: #遍历每一个ticketID
        cnt+=1
        print("第" + str(cnt) + "个ID..." + "     当前时间：" + str(time.asctime(time.localtime(time.time()))))
        #if cnt % 1000 ==0:
            #print("     进度: " + str(float(1.0*cnt/len(uniqueTicketList))))
            #print("     当前时间：" + str(time.asctime(time.localtime(time.time()))))
        if pseries[psg] >= 4:
            trps = trips.loc[psg]
            sampleArr = []
            count = 0
            for v in trps.values:
                sampleArr.append([])
                sampleArr[count].append(getTimeCode(v[0]))
                sampleArr[count].append(getDestNameCode(v[1]))
                count += 1
            X = np.array(sampleArr)
            db = skc.DBSCAN(eps=EPS_SET, min_samples=4).fit(X)  # DBSCAN聚类方法 还有参数，eps=eps_set=15,代表分钟 min_samples=4代表个数
            labels = db.labels_
            # Sugh: 后面的结果统计在这之后修改
            n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # 获取分簇的数目
            raito = len(labels[labels[:] == -1]) / len(labels)  # 计算噪声点个数占总数的比例
            if n_clusters_ > 0:  # 有至少一个聚类的结果
                for i in range(n_clusters_):  # 在生成的簇间循环
                    data_sql.append([])
                    one_cluster = X[labels == i]
                    mingzi = one_cluster[0][1]
                    chud = DestNameDictRev[mingzi]  # OD对转码
                    OD = chud.split('-')
                    O = OD[0]
                    D = OD[1]  # 将OD对拆分成O和D两部分
                    shijian1 = min(one_cluster[:, 0])  # 同一簇里时间最小值
                    shijian2 = max(one_cluster[:, 0])  # 同一簇里时间最大值
                    h1 = shijian1 // 60
                    m1 = shijian1 % 60
                    h2 = shijian2 // 60
                    m2 = shijian2 % 60
                    # 将时间转码，转成小时和分钟的形式
                    ODt = [str(psg), i, str(h1) + ':' + str(m1), str(h2) + ':' + str(m2), O, D, len(one_cluster), raito]
                    #第一项为乘客ID；第二项为簇号；第三项为时间段起始时间；第四项为时间段结束时间；第五项为进站名；第六项为出站名；第七项为样本数；最后一项为噪声比
                    data_sql[n].append(str(ODt[0]))  # 乘客ID号
                    data_sql[n].append(str(ODt[1]))  # 簇号
                    data_sql[n].append(str(ODt[2]))  # 时间段起始时间
                    data_sql[n].append(str(ODt[3]))  # 时间段结束时间
                    data_sql[n].append(str(ODt[4]))  # 进站名称
                    data_sql[n].append(str(ODt[5]))  # 出站名称
                    data_sql[n].append(str(ODt[6]))  # 样本数
                    data_sql[n].append(str(ODt[7]))  # 噪声比
                    n = n + 1
        else:
            a = 1  ##Sugh: 在这里处理小于4次的情况
    #Sugh: 写数据库用pd.to_sql(insert语句)
    for d_sql in data_sql:
        if d_sql:
            curs2.execute("insert into midu_all_jieguo(TICKET_ID,CLUSTER_NUMBER,START_TIME,END_TIME,\
                          IN_STATION_NAME,TXN_STATION_NAME,SAMPLE_NUMBER,NOISE_RATION) values('" + str(d_sql[0]) + "','" + \
                          str(d_sql[1]) + "','" + str(d_sql[2]) + "','" + str(d_sql[3]) + "','" + str(d_sql[4]) \
                          + "','" + str(d_sql[5]) + "','" + str(d_sql[6]) + "','" + str(d_sql[7]) + "')")
            conn2.commit()
            # 聚类结果输入数据库
    print("结束,当前时间：" + str(time.asctime(time.localtime(time.time()))))
    print(n)
#程序入口
usr = "root"
pwd = "chm123"
db = "bjtu"
#sqlstr = "select OOOO, TXN_STATION_NAME from C201907_t where rownum < 100"
sqlstr = "select TICKET_ID,OOOO,OD_dui from od_dui order by TICKET_ID"#where ticket_id  like '0021500025576%'# ='0021500025576195' or ticket_id ='0021500025458751'"# rownum < 20"# order by ticket_id"
print("开始时间：" + str(time.asctime(time.localtime(time.time()))))
process(sqlstr, usr, pwd, db)  #

