from rest_framework.response import Response
from rest_framework import mixins, generics, status
from django.http.response import HttpResponse
from .models import *
import pandas
from pandas import DataFrame,Series
import json
import pandas as pd
import re
import pymysql

class Distribution(generics.GenericAPIView):

    def get(self, request):
        params = request.query_params.get('params').split(',')
        return Response(self.result_by_any(params[0],params[1]+'：',int(params[2]),int(params[3])))

    def read_data(self):
        a = open('analysis/female2.txt', encoding='UTF-8-sig')
        b = a.read()
        c = b.split('\n')[:-1]
        users = []
        for i in c:
            d = i.replace("'", '"').replace('\\', '')
            e = json.loads(d)
            users.append(e)
        return users

    def result_by_any(self, by_str, result, begin, end):
        users = self.read_data()
        sets = list()
        for i in users:
            if begin <= int(i[by_str][:2]) <= end:
                if i[result] not in sets:
                    sets.append(i[result])
        count = dict.fromkeys(sets,0)
        for i in users:
            if begin <= int(i[by_str][:2]) <= end:
                count[i[result]] += 1

        total = sum(count.values())
        distribution = {}
        for key, value in count.items():
            distribution[key] = [value, '%.0f%%' % (value / total * 100)]
        return distribution


class API1(generics.GenericAPIView):

    def get(self,request):
        # pd.set_option('display.width', 10000)
        # pd.set_option('display.max_rows', 500)
        # pd.set_option('display.max_columns', 500)
        params = request.query_params.get('params').split(',')
        usersR = self.get_analyis_data_by_score(params[0],params[1],params[2])
        return usersR


    def query_users(self):
        db = pymysql.connect(host='localhost', user='root', password='JCheng123', port=3306,db='spiders6')
        cursor = db.cursor()
        sql = 'SELECT * FROM ustest2'
        columns = []
        users2 = []
        try:
            cursor.execute(sql)
            users = cursor.fetchall()
            cols = cursor.description
            db.close()
            for col in cols:
                column = col[0]
                columns.append(column)
            for user in users:
                users2.append(user)
        except Exception as e:
            print(e)
        db.close()
        return users2,columns

    def get_analyis_data_by_score(self,SBeign,SEnd,attr):
        users,cols = self.query_users()
        usersDF = pd.DataFrame(users,columns=cols)
        usersDF['分数'] = usersDF['分数'].astype('int')
        usersAS = usersDF[usersDF['分数'] > SBeign][usersDF['分数'] < SEnd]
        userASHeight = usersAS[attr].value_counts()
        userASHeightDF = pd.DataFrame(userASHeight)
        userASHeightDF['频率'] = userASHeightDF/userASHeightDF[attr].sum()
        return userASHeightDF.to_dict()



