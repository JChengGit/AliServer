from rest_framework.response import Response
from rest_framework import mixins, generics, status
from django.http.response import HttpResponse
from .models import *
import json
import pandas
from pandas import DataFrame,Series

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
