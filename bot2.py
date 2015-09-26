#!/usr/bin/env python                                                                                                                                             
# -*- coding:utf-8 -*-                                                                                                                                            

import urllib3
import datetime
import re
import json
import sqlite3
import time
from requests_oauthlib import OAuth1Session
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit



#   ＿人人人人人人人人＿
#   ＞ここからtwitter ＜
#   ￣^Y^Y^YY^Y^Y^Y￣

oath_key_dict = {
    "consumer_key": "qtQofYXpfbuN0hNTCI5uWSgJY",
    "consumer_secret": "W3EhHzzIf08QocZ9yNS55sxQEGDus0wTLO5qKAOhs7SHFNfemO",
    "access_token": "3193141501-OZUG2QLhI83nwDQYbf5DGvQkaZ3jSc8zlDqUFg3",
    "access_token_secret": "WoMdd7ksQJ3O1eYJYYIyK2zc9xY7ykVpxtyayOG1aO7Ve"
}

class Tweet:
    def _search(self,search_word):
        tweets = tweet_search(search_word, oath_key_dict)
        for tweet in tweets["statuses"]:
            tweet_id = tweet[u'id_str']
            text = tweet[u'text']
            created_at = tweet[u'created_at']
            user_id = tweet[u'user'][u'id_str']
        user_description = tweet[u'user'][u'description']
        screen_name = tweet[u'user'][u'screen_name']
        user_name = tweet[u'user'][u'name']
        print "tweet_id:", tweet_id
        print "text:", text
        print "created_at:", created_at
        print "user_id:", user_id
        print "user_desc:", user_description
        print "screen_name:", screen_name
        print "user_name:", user_name
        return


    def _create_oath_session(self,oath_key_dict):
        oath = OAuth1Session(
        oath_key_dict["consumer_key"],
        oath_key_dict["consumer_secret"],
        oath_key_dict["access_token"],
        oath_key_dict["access_token_secret"]
        )
        return oath

    def _tweet_search(self,search_word, oath_key_dict):
        url = "https://api.twitter.com/1.1/search/tweets.json?"
        params = {
            "q": unicode(search_word),
            "result_type": "recent",
            "count": "15"
            }
        oath = create_oath_session(oath_key_dict)
        responce = oath.get(url, params = params)
        if responce.status_code != 200:
            print "Error code: %d" %(responce.status_code)
            return None
        tweets = json.loads(responce.text)
        return tweets
    
    def _tweet_post(self,text):
        url = "https://api.twitter.com/1.1/statuses/update.json"
        params = {"status": text}
        oath = self.create_oath_session(oath_key_dict)
        responce = oath.post(url, params = params)






#   ＿人人人人人人人人＿
#   ＞　ここからParse ＜
#   ￣^Y^Y^YY^Y^Y^Y￣



class Parse:
    def __init__(self):
        self.soup_obj = None
        self.url = ""
        self.brand_name = ""
        self.date = ""
        self.latest_news = ""
        self.old_news = ""
        self.enable = 0
        self.recode_idx = 0
        self.recode_count = 0
        self.DB = None
        self.change_flag = False

        #HTMLからオブジェクトを作成
    def __set_obj(self):
        http = urllib3.PoolManager()
        html = http.request('GET',self.url)
        response = html.data
        self.soup_obj = BeautifulSoup(response)
        print "setted obj"
    
    def __check_obj(self):
        if self.soup_obj is None:
            print "No obj"
            return False
        print "obj is exist"
        return True
    
    def __reset_values(self):
        self.url = ""
        self.brand_name = "なし"
        self.latest_news = "なし"
        self.old_news = "なし"
        self.soup_obj = None




    ##########################
    ### メーカー毎のパース処理 ###
    ##########################
    
    def __select_parser(self):
        n = self.recode_idx
            #DBの番号に応じて選択する
        i = 12 if n >12 else int(n)
        [
            (lambda self: None), #DBのidxに合わせて1から処理をつける
            (lambda self: self.__set_feng()),
            (lambda self: self.__set_yuzusoft()),
            (lambda self: self.__set_pallet()),
            (lambda self: self.__set_innocent_grey()),
            (lambda self: self.__set_alcot()),
            (lambda self: self.__set_axl()),
            (lambda self: self.__set_ensemble()),
            (lambda self: self.__set_pulltop()),
            (lambda self: self.__set_hooksoft())
            ][i](self)
    
            
    def __set_feng(self):
            #1ニュース分の1つ目の複数のtdを取得
        news = self.soup_obj.find("table",id="news").tr
            #それらの兄弟tdの文章を取得
        for idx,string in enumerate(news.stripped_strings):
                #日付があるtdタグを選択
            if idx == 1:
                self.date = string
                #更新内容があるtdタグを選択
            if idx == 2:
                self.latest_news = string
            if idx == 3:        #記事によってbreakするidxが変わる可能性あり
                break

    def __set_yuzusoft(self):
            #1ニュース分の1つ目のdlを取得
        news = self.soup_obj.find("div",class_="update-frame")
        self.date = news.dt.get_text()
        self.latest_news = news.dd.get_text()
    
    def __set_pallet(self):
        news = self.soup_obj.find("dl")
        self.date = news.dt.get_text()
        self.latest_news = news.dd.get_text()
    
    def __set_innocent_grey(self):
            #1ニュース分の1つ目の複数のtdを取得
        news = self.soup_obj.find("tr")
            #それらの兄弟tdの文章を取得
        for idx,string in enumerate(news.stripped_strings):
                #日付があるtdタグを選択
            if idx == 0:
                self.date = string
                #更新内容があるtdタグを選択
            if idx == 1:
                self.latest_news = string
            if idx == 2:    #記事によってbreakするidxが変わる可能性あり
                break
    
    def __set_alcot(self):
        news = self.soup_obj.find("div",id="news").dl
        self.date = news.dt.get_text()
        self.latest_news = news.dd.get_text()

    def __set_axl(self):
        news = self.soup_obj.find("table",class_="news")
        for idx,string in enumerate(news.stripped_strings):
            if idx == 0:
                self.date = string
            if idx == 2:
                self.latest_news = string
            if idx == 4:    #記事によってbreakするidxが変わる可能性あり
                break
    
    def __set_ensemble(self):
        news = self.soup_obj.find("table")
        for idx,string in enumerate(news.stripped_strings):
            if idx == 0:
                date = string
            if idx == 2:
                self.latest_news = string
            if idx == 4:
                self.latest_news = self.latest_news + string
            if idx == 5:
                self.latest_news = self.latest_news + string
            if idx ==6:     #breakするタイミングが記事によって異なるため注意
                break

    def __set_pulltop(self):
        news = self.soup_obj.find("dl")
        self.date = news.dt.get_text()
        self.latest_news = news.dd.get_text()

    def __set_hooksoft(self):
        news = self.soup_obj.find("p",class_="life")
        self.date = news.get_text()[0:10]
        self.latest_news = news.get_text()[11:].rstrip()
        self.latest_news = self.latest_news.replace(" ","").replace("-","")






#   ＿人人人人人人人人＿
#   ＞　ここからDB  ＜
#   ￣^Y^Y^YY^Y^Y^Y￣



    #################
    ### DB schema ###
    #################
    '''
    CREATE TABLE brands(idx INTEGER PRIMARY KEY,
        brand_name TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL UNIQUE,
        latest_news TEXT,
        enable INTEGER default 0,
        modified TEXT);
    '''
    ### ※DBのidxは1からはじまる ###
    
    def __connectDB(self):
        con = sqlite3.connect("botDB.sqlite3")#DB接続
        self.DB = con
        print "connect DB OK"

    def __closeDB(self):
        self.DB.close()
        print "close DB OK"
    
    def __recode_count(self):
        c = self.DB.cursor()
            #全レコード件数を取得
        c.execute("""SELECT COUNT(*) FROM brands;""")
        self.recode_count = c.fetchone()[0]
        print "recode count OK"

    def __readDB(self):
            #カーソルを当てる
        c = self.DB.cursor()
            #全件読み込み
        c.execute(u"select * from brands")
            #レコード1件を取得  (#idx,ブランド名,URL,最新news,有効,更新日時)
        row = c.fetchall()[self.recode_idx-1] #取得したレコードは最初が0から始まる
        self.brand_name = row[1]
        self.url = row[2]
        self.old_news = row[3]
        self.enable = row[4]
        print "read DB OK"

    def __updateDB(self):
        if self.change_flag:
            d = datetime.datetime.today()
            c = self.DB
                #更新日付と最新更新内容の更新(query)
                #c.execute('''UPDATE brands SET latest_news=?,modified=? WHERE idx=?''',
                #        (self.latest_news.encode('utf-8'),d.strftime("%x %X"),self.recode_idx))
            update_sql = "UPDATE brands SET latest_news=?, modified=? WHERE idx=?;"
            fact = [self.latest_news,d.strftime("%Y/%m/%d %H:%M:%S"),self.recode_idx]
            c.execute(update_sql,fact)
            c.commit()
            print "update DB OK"
        return

    def __judge_change(self):
        self.change_flag = False if self.old_news == self.latest_news else True
        print "=======> "+self.brand_name + ":" + str(self.change_flag)





#   ＿人人人人人人人人＿
#   ＞ ツイート生成 ＜ 
#   ￣^Y^Y^YY^Y^Y^Y￣
    def __create_tweet(self):
        tweet = Tweet()
        tweet.tweet_post( "更新情報\n".decode('utf-8')+
                "メーカー:".decode('utf-8') + self.brand_name + 
                "\n" + self.date + ":" + self.latest_news +"\n")
        print "Tweet OK"





#   ＿人人人人人人人人＿
#   ＞ここから呼び出し ＜
#   ￣^Y^Y^YY^Y^Y^Y￣


        #__onchange() 変更があったら、DBのアップデートとツイートをする
    def __onchange(self):
        if self.change_flag:
                self.__updateDB()
                self.__create_tweet()

        
    def __exist_obj(self):
            #soupオブジェクトが存在していることを確認
        if self.__check_obj():
            self.__select_parser()  #__select_parser() recode_idxをもとにメーカー毎のパース処理を呼び出す
            self.__judge_change()   #__judge_change() 以前の内容と最新の内容が異なるか判断
            self.__onchange()
        return

    def __affair(self):
        self.__readDB()
                #enableのメーカーはオブジェクトを生成しないで終了する。
        if self.enable != 0:    #DBの実行フラグを確認
            self.__set_obj()    #soupオブジェクトを生成
            self.__exist_obj()  #オブジェクトが正常に存在するかを確認&パースの実行
            self.__reset_values()   #一度変数をリセット消す。 パースが実行されていないのがわかりやすいように。

    def __start(self):
        print "start..."
        self.__recode_count()   #__recode_count() DBに何件のレコードがあるかを取得 -> recode_count
        for i in range(1,self.recode_count+1):
            self.recode_idx = i
            self.__affair()
    
    def update(self):
        self.__connectDB()
        self.__start()
        self.__closeDB()
        print "All done"





#   ＿人人人人人人人人＿
#   ＞　ここからMain ＜
#   ￣^Y^Y^YY^Y^Y^Y￣



if __name__ == "__main__":
    parse = Parse()
    parse.update()
    tweet = Tweet()