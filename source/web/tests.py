#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__ : stray_camel
#pip_source : https://mirrors.aliyun.com/pypi/simple
import sys,os
import pandas as pd
import numpy as np
from django.conf import settings
# 线程池
from concurrent.futures import ThreadPoolExecutor
# fix error : _csv.Error: field larger than field limit (131072)
import csv
maxInt = sys.maxsize
while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)
# 本想调用django中settings的base_dir的，但是由于需要此文件独立django运行，所以加上try except来当独立运行时，可以自己赋值
try:
    BASE_DIR = settings.BASE_DIR
except:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CF_CB():
    '''
    Collaborative Filtering + Content-based Filtering
    '''
    def __init__(self):
        self.load_data()
    
    def save_data(self, 
        data: "{'数据名1':'数据1'，'数据名2':'数据2'}",
        )->"保存到tmp/Matrix_factorization文件夹，方便查看":
        def saving(processed_data, path):
            processed_data.to_csv(path, sep='\t', header=True, index=True)
        executor = ThreadPoolExecutor(max_workers=20)
        for name,data in data:
            # 利用线程池--concurrent.futures模块来管理多线程：
            future = executor.submit(saving,data,os.path.dirname(BASE_DIR)+'/tmp/Matrix_factorization'+name+'.csv')
    
    def process_data(self):
        '''
        初始化所有数据
        books, tags, users 为去重后的list
        book_tag = {'book':[],'given_tag':[]} 为所有用户历史行为中，book被基于的标签
        UBdata: index=users,columns=books
        UTdata: index=users,columns=tags
        TBdata: index=books,columns=tags
        '''
        book_tag = {'book':[],'given_tag':[]}
        books = []
        tags = []
        user_s = pd.read_csv(os.path.dirname(BASE_DIR)+'/data/users.csv', nrows=5, sep='\t', engine='python', dtype={'history':dict})
        users = list(user_s['user'])
        for _ in user_s['history']:
            try:
                books.extend(set(_['book']))
                tags.extend(set(_['given_tag']))
                book_tag.append(_)
            except TypeError as e:
                books.extend(set(eval(_)['book']))
                tags.extend(set(eval(_)['given_tag']))
                book_tag['book']+=eval(_)['book']
                book_tag['given_tag']+=eval(_)['given_tag']
        books.sort()
        books = list(set(books))
        tags.sort()
        tags = list(set(tags))

        # UBdata: index=users,columns=books
        UBdata = [[eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['book'].count(int(b)) if b in eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['book']  else 0 for b in books] for u in users]
        user_books = pd.DataFrame(UBdata,index=users,columns=books)

        # UTdata: index=users,columns=tags
        UTdata = [[eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['given_tag'].count(int(t)) if t in eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['given_tag']  else 0 for t in tags] for u in users]
        users_tags = pd.DataFrame(UTdata,index=users,columns=tags)
        
        # TBdata: index=books,columns=tags
        TBdata = np.zeros((len(tags),len(books)))
        # value = tuple(zip(*list(book_tag.values3w
        # TBdata[rows, cols] = counts
        for b_i,b_v in enumerate(book_tag['book']):
            t_v=book_tag['given_tag'][b_i]
            TBdata[tags.index(t_v),books.index(b_v)] +=1
        tags_books = pd.DataFrame(TBdata,index=tags,columns=books)


    def load_data(self):
        '''
        初始化所有数据
        self.books, self.tags, self.users 为去重后的list
        self.book_tag = {'book':[],'given_tag':[]} 为所有用户历史行为中，book被基于的标签
        self.UBdata: index=users,columns=self.books
        self.UTdata: index=users,columns=self.tags
        self.TBdata: index=self.books,columns=self.tags
        '''
        self.book_tag = {'book':[],'given_tag':[]}
        self.books = []
        self.tags = []
        user_s = pd.read_csv(os.path.dirname(BASE_DIR)+'/data/users.csv', nrows=5, sep='\t', engine='python', dtype={'history':dict})
        users = list(user_s['user'])
        for _ in user_s['history']:
            try:
                self.books.extend(set(_['book']))
                self.tags.extend(set(_['given_tag']))
                self.book_tag.append(_)
            except TypeError as e:
                self.books.extend(set(eval(_)['book']))
                self.tags.extend(set(eval(_)['given_tag']))
                self.book_tag['book']+=eval(_)['book']
                self.book_tag['given_tag']+=eval(_)['given_tag']
        self.books.sort()
        self.books = list(set(self.books))
        self.tags.sort()
        self.tags = list(set(self.tags))

        # self.UBdata: index=users,columns=self.books
        self.UBdata = [[eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['book'].count(int(b)) if b in eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['book']  else 0 for b in self.books] for u in users]
        user_books = pd.DataFrame(self.UBdata,index=users,columns=self.books)

        # self.UTdata: index=users,columns=self.tags
        self.UTdata = [[eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['given_tag'].count(int(t)) if t in eval(list(user_s.loc[user_s['user'] == u,'history'])[0])['given_tag']  else 0 for t in self.tags] for u in users]
        users_tags = pd.DataFrame(self.UTdata,index=users,columns=self.tags)
        
        # self.TBdata: index=self.books,columns=self.tags
        self.TBdata = np.zeros((len(self.tags),len(self.books)))
        # value = tuple(zip(*list(self.book_tag.values3w
        # self.TBdata[rows, cols] = counts
        for b_i,b_v in enumerate(self.book_tag['book']):
            t_v=self.book_tag['given_tag'][b_i]
            self.TBdata[self.tags.index(t_v),self.books.index(b_v)] +=1
        self.tags_books = pd.DataFrame(self.TBdata,index=self.tags,columns=self.books)
        print ("----------- 1、load data -----------")

    def gradAscent(self, 
        alpha:'alpha(float):学习率'=0.0002, 
        beta:'beta(float):正则化参数'=0.02, 
        maxCycles:'maxCycles(int):最大迭代次数'=50,
        )->'p,q(mat):分解后的矩阵':
        '''
        利用梯度下降法对矩阵进行分解
        '''
        dataMat = np.mat(self.UBdata)
        # 5*5的矩阵
        m, n = np.shape(dataMat)
        # 1、初始化p和q，分解成两个矩阵 m*k,k*n 
        p = np.mat(self.UTdata)
        q = np.mat(self.TBdata)
        # k(int):分解矩阵的参数,分解成两个矩阵 m*k,k*n 
        k = len(self.tags)
        # 2、开始训练
        for step in range(maxCycles+1):
            for i in range(m):
                for j in range(n):
                    if dataMat[i, j] > 0:
                        # 求出每个点的差值
                        error = dataMat[i, j]
                        for r in range(k):
                            error = error - p[i, r] * q[r, j]
                        for r in range(k):
                            # 梯度上升
                            try:
                                p[i, r] = p[i, r] + alpha * (2 * error * q[r, j] - beta * p[i, r])
                                q[r, j] = q[r, j] + alpha * (2 * error * p[i, r] - beta * q[r, j])
                            except OverflowError:
                                pass
                            
            loss = 0.0
            for i in range(m):
                for j in range(n):
                    if dataMat[i, j] > 0:
                        error = 0.0
                        for r in range(k):
                            error = error + p[i, r] * q[r, j]
                        # 3、利用square loss计算损失函数
                        loss = (dataMat[i, j] - error) * (dataMat[i, j] - error)
                        #L1正则化是指权值向量w中各个元素的绝对值之和
                        #L2正则化是指权值向量w中各个元素的平方和然后再求平方根
                        for r in range(k):
                            loss = (loss + beta * (p[i, r] * p[i, r] + q[r, j] * q[r, j])) / 2
            if loss < 0.001:
                break
            if step % 10 == 0:
                print ("\titer: ", step, " loss: ", loss)
        print ("----------- 2、training - 利用梯度下降法对矩阵进行分解 -----------")
        return p, q

    def prediction(self):
        '''为用户user未互动的项打分
        input:  dataMatrix(mat):原始用户商品矩阵
                p(mat):分解后的矩阵p
                q(mat):分解后的矩阵q
                user(int):用户的id
        output: predict(list):推荐列表
        '''
        user = 0
        p, q = self.gradAscent()
        dataMatrix = dataMat = np.mat(self.UBdata)
        n = np.shape(dataMatrix)[1]
        predict = {}
        for j in range(n):
            if dataMatrix[user, j] == 0:
                predict[j] = (p[user,] * q[:,j])[0,0]
        
        # 按照打分从大到小排序
        print ("----------- 3、prediction -----------")
        return sorted(predict.items(), key=lambda d:d[1], reverse=True)

    def top_k(self):
        '''为用户推荐前k个商品
        input:  predict(list):排好序的商品列表
                k(int):推荐的商品个数
        output: top_recom(list):top_k个商品
        '''
        predict = self.prediction()
        k = 5
        top_recom = []
        len_result = len(predict)
        if k >= len_result:
            top_recom = predict
        else:
            for i in range(k):
                top_recom.append(predict[i])
        print ("----------- 4、top_k recommendation ------------")
        return top_recom
    
if __name__ == "__main__":
    test = CF_CB()
    print(test.top_k())
    