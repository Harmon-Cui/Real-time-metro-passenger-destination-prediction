import requests
import json
import pprint
import pandas as pd
import csv
import pprint

key = 'YOUR_AMAP_API_KEY'  # 填入自己的key


# 构建函数
def getlnglat(address):
    #url = 'https://restapi.amap.com/v3/geocode/geo'
    url = 'https://restapi.amap.com/v3/geocode/geo'
    params = {'key': key,
              'address': address}
    res = requests.get(url, params)
    json_data = json.loads(res.text)
    return json_data


# 打开cs
inpath = r"C:/Users/Harmony\Desktop/南京地铁站点全称.csv"
outpath = r"C:/Users/Harmony\Desktop/南京地铁站经纬度获取结果.xlsx"
df = pd.read_csv(inpath, encoding='UTF-8')
df['lng'] = 'collng'  # 创建新列存放经度
df['lat'] = 'collat'  # 创建新列存放纬度
n = 0
for i in df.values:
    print(i)
    b = i[0]  # 第一列的地址 .strip("'")
    ind = n
    print(b)
    json_data = getlnglat(b)
    print(json_data)
    i[1] = json_data['geocodes'][0]['location']  # 获取经纬度
    lng_i = float(str(i[1]).split(",")[0])
    lat_i = float(str(i[1]).split(",")[1])
    df.loc[ind,'lng'] = lng_i  # 经度
    df.loc[ind,'lat'] = lat_i  # 纬度
    pprint.pprint(json_data)
    n = n + 1

df.to_excel(outpath)


