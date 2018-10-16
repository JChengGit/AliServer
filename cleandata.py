import json
import pandas as pd
import re
import mysqlclient

# 清洗数据后存入DB
file_name = 'out.txt'

score_weight = {'住房：':{'已购住房 ': 25, '需要时购置 ': 15, '独自租房 ': 8, '已购房（无贷款） ': 30, '已购房（有贷款） ': 20,
             '与父母同住 ': 10, '暂未购房 ': 5, '住单位房 ': 18, '住亲朋家 ':2 , '与人合租 ': 2, '-- ': 10},
                '购车：':{'单位用车 ': 13, '暂未购车 ': 4, '需要时购置 ': 5, '已购车（经济型） ': 8, '已经购车 ': 8,
             '已购车（中档型） ': 12, '已购车（豪华型） ': 15, '-- ': 5, },
                '学历：':{'高中中专及以下': 1, '大专': 2, '本科': 5, '硕士': 8, '博士': 10, '-- ': 4, },
                '月薪：':{'2000元以下 ': 5, '2000～5000元 ': 12, '5000～10000元 ': 15, '10000～20000元 ': 20,
             '20000～50000元 ': 26, '50000元以上 ': 30, '-- ': 12, }}
def score_height(height):
    try:
        heightstr = re.findall(r'[0-9]*cm', height)
        heightstr = heightstr[0]
        heightstr = heightstr[0:3]
        if 160 <= int(heightstr) < 165:
            return 1
        elif 165 <= int(heightstr) < 170:
            return 2
        elif 170 <= int(heightstr) < 175:
            return 3
        elif 175 <= int(heightstr) < 180:
            return 4
        elif 180 <= int(heightstr) < 190:
            return 5
        else:
            return 0
    except Exception as e:
        print(e)

def score_BMI(height,weight):
#     体质指数（BMI）=体重（kg）÷身高^2（m）
#     当BMI指数为18.5～23.9时属正常。
    try:
        heightstr = re.findall(r'[0-9]*cm', height)
        heightstr = heightstr[0]
        heightstr = heightstr[0:3]
        weightstr = re.findall(r'[0-9]*公斤', weight)
        weightstr = heightstr[0]
        weightstr = heightstr[0:2]
        BMI = weightstr / (int(heightstr) * int(heightstr))
        if 18.5 < BMI < 24:
            return 1
        else:
            return 0
    except Exception as e:
        return 0

def read_data():
    # 之后的数据来源为数据库，并且参数提供查询的条件，读出来的数据的按照参训条件去读
    a = open(file_name, encoding='UTF-8-sig')
    b = a.read()
    c = b.split('\n')[:-1]
    users = []
    for i in c:
        d = i.replace("'", '"').replace('\\', '')
        e = json.loads(d)
        e['age'] = e['age'][0:2]
        users.append(e)
    users = score_user(users)
    return users

def score_user(users):
    # 对用户进行打分
    users_af_score = []
    sets = list()
    for i in users:
        try:
            i['分数'] = 0
            i['分数'] += score_weight['学历：'][i['学历：']]
            i['分数'] += score_weight['购车：'][i['购车：']]
            i['分数'] += score_weight['住房：'][i['住房：']]
            i['分数'] += score_weight['月薪：'][i['月薪：']]
            i['分数'] += score_height(i['身高：'])
            i['分数'] += score_BMI(i['身高：'],i['体重：'])
        except Exception:
            i['分数'] = 0
        users_af_score.append(i)
    return users_af_score

# 运行创建表
def create_table():
    db = pymysql.connect(host='localhost', user='root', password='JCheng123', port=3306)
    cursor = db.cursor()

    cursor.execute("CREATE DATABASE spiders6 DEFAULT CHARACTER SET utf8")
    db.close()
    db = mysqlclient.connect(host='localhost', user='root', password='root', port=3306,db='spiders6')
    cursor = db.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS ustest2 (id varchar(255) NOT NULL,' \
          '月薪 varchar(255) ,住房 varchar(255) ,购车 varchar(255) ,' \
          '学历 varchar(255) ,体重 varchar(255) ,身高 varchar(255) ,' \
          '分数 varchar(255) ,年龄 varchar(255) )'
    cursor.execute(sql)
    db.close()

def save_db(users):
    db = mysqlclient.connect(host='localhost', user='root', password='root', port=3306,db='spiders6')
    cursor = db.cursor()
    table = 'ustest2'
    for user in users:
        keys =','.join(user.keys())
        values = ','.join(['%s'] * len(user))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table =table,keys = keys,values = values)
        # sql = 'INSERT INTO ustest2(id,月薪) values(%s,%s)'
        try:
            # if cursor.execute(sql,(user['id'],user['月薪'])):
            if cursor.execute(sql,tuple(user.values())):
                print('成功')
                db.commit()
        except Exception as e:
            print('失败')
            print(e)
            db.rollback()

def convert_dict(users):
    users_new = []
    for user in users:
        users_new_line = {}
        users_new_line['id'] = user['id']
        users_new_line['月薪'] = user['月薪：']
        users_new_line['住房'] = user['住房：']
        users_new_line['购车'] = user['购车：']
        users_new_line['学历'] = user['学历：']
        users_new_line['体重'] = user['体重：']
        users_new_line['身高'] = user['身高：']
        users_new_line['年龄'] = user['age']
        users_new_line['分数'] = user['分数']
        users_new.append(users_new_line)
    return users_new



# 第一次使用create_table()创建db
# create_table()#创建数据库以及所需的表
users = read_data()
users = convert_dict(users)
save_db(users)



