#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import datetime
dt_now = datetime.datetime.now()

# URLの定義 RSS for sciencemagazine
urls = [
    'https://science.sciencemag.org/rss/ec.xml',
    'https://science.sciencemag.org/rss/current.xml',
    'https://science.sciencemag.org/rss/twis.xml',
    'https://science.sciencemag.org/rss/express.xml',
    'https://www.sciencemag.org/rss/news_current.xml',
    'https://advances.sciencemag.org/rss/current.xml',
    'https://robotics.sciencemag.org/rss/current.xml'
]
from feedparser import parse
from datetime import datetime as dt
from googleapiclient.discovery import build
###############################################
googlekey="************************************" #←Google Cloud からキーを入れてください。有料サービス。上のＲＳＳだけなら月３００円くらいです。
#Google翻訳ＡＰＩ# https://cloud.google.com/translateを使います
#
#################################################
def translaltion(source, target, words):
  # Build a service object for interacting with the API. Visit
  # the Google APIs Console <http://code.google.com/apis/console>
  # to get an API key for your own application.
    service = build('translate', 'v2',
            developerKey=googlekey)
    ss=(service.translations().list(
      source=source,
      target=target,
      q=[words]
    ).execute())
    print (ss)
    translated=ss['translations'][0]['translatedText']
    return translated
# 日付のパース用関数
def parseDate(dateData):
    return dt(
        dateData.tm_year,
        dateData.tm_mon,
        dateData.tm_mday,
        dateData.tm_hour,
        dateData.tm_min,
        dateData.tm_sec)

# リスト内包表記でサクッと取得&整形
entries = [
    {
        'title': entry['title'],
        'link': entry['link'],
        'description': entry['description'],
        'date': parseDate(entry['updated_parsed'] or entry['published_parsed'])
    }
    for url in urls
    for entry in parse(url).entries
]
#rss.xlsxを読む 翻訳をしたものを記録します。重複して翻訳しないように。
df=pd.read_excel('./scienceRSS/rss_history.xlsx',index_col=0)

# 日付順でソート
entries.sort(key=lambda x: x['date'], reverse=True)
df_new=pd.DataFrame(columns=["title","titleJPN","description","descriptionJPM","date","link"])
savedEntries = []
n=len(df)
#RSSから得たデータ。不要なコードを消します
NGwords=["?rss=1","&gt;","<I>","</I>","</I>,","<SUB>","</SUB>","&ndash;","<P>","</P>","<p>","</p>","<I>","<sup>","</sup>","</i> ","&ndash","<SUB>","</sub> ","<sub> "," {degrees}","</sub> ","<sub> ","<f>","</f>"]
for entry in entries:
# タイトルを表示して、
    finddb=df[df["title"]==entry['title']]
    print (entry['title'])
    if len(finddb)==0:
        df.loc[n,"title"]=entry['title']
        df.loc[n,"link"]=entry['link']
        entrydescription=entry['description']
        for wd in NGwords:
            entrydescription=entrydescription.replace(wd,"")
        df.loc[n,"description"]=entrydescription
        df.loc[n,"date"]=entry['date']
        df_new.loc[n,"title"]=entry['title']
        df_new.loc[n,"link"]=entry['link']
        df_new.loc[n,"description"]=entrydescription
        df_new.loc[n,"date"]=entry['date']
        df_new.loc[n,"titleJPN"]=translaltion("en","ja",entry['title'])
        if len(entrydescription)>0:
            df_new.loc[n,"descriptionJPM"]=translaltion("en","ja",entrydescription)
        else:
            df_new.loc[n,"descriptionJPM"]=""
        #df_new.loc[n,"titleJPN"]=""
        #df_new.loc[n,"descriptionJPM"]=""
        n=n+1
        print (n)
    else:
        print ("skip")
#############
#ファイルの作成
#scienceRSSフォルダーの下に過去ログ(rss_history.xlsx)と
#今回翻訳した分(rss_transaction_{}{}{}.xlsx)をつくります。
df.to_excel('./scienceRSS/rss_history.xlsx', sheet_name='new_sheet_name')
df_new.to_excel('./scienceRSS/rss_transaction_{}{}{}.xlsx'.format(dt_now.month,dt_now.day,dt_now.hour), sheet_name='new_sheet_name')
print ("end")
