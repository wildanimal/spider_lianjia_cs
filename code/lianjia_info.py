# _*_coding:utf-8_*_
import time
import requests
from pub_fuc import re_fuc
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

client = MongoClient()
dbName = 'lianjia'
dbTable = 'xiaoqu'
tab = client[dbName][dbTable]
dbTable2 = 'xiaoqu_detail_0916'
tab2 = client[dbName][dbTable2]

def getresp(req, retries = 2):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'cs.lianjia.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
        }

        ses = requests.session()
        ses.get('http://cs.lianjia.com/xiaoqu/rs/')
        html = ses.post(req, headers=headers)
        data = html.text.encode('iso8859-1').decode('utf-8')
    except Exception, what:
        print what, req
        if retries > 0:
            return getresp(req, retries - 1)
        else:
            print 'GET Failed', req
            return ''
    return data


xiaoqus = tab.find()
for x in xiaoqus:
    if x:
        url = x['url']
        print url
        if not tab2.find_one({'url': url}):
            cont = getresp(url)
            print(cont)

            rel = [r'<h1 class="detailTitle">(.*?)</h1><div class="detailDesc">(.*?)</div>[\s\S]*?<a href="/xiaoqu/">(.*?)</a>[\s\S]*?<a href=[\s\S]*?>(.*?)</a>[\s\S]*?<a href=[\s\S]*?>(.*?)</a>[\s\S]*?<span class="xiaoquInfoLabel">' + u'建筑年代' \
                   + r'</span><span class="xiaoquInfoContent">(.*?)' + u'年建成' + r'[\s\S]*?<span class="xiaoquInfoLabel">' \
                   + u'建筑类型' + r'</span><span class="xiaoquInfoContent">(.*?)</span>[\s\S]*?class="xiaoquInfoContent">(.*?)</span>[\s\S]*?class="xiaoquInfoContent">(.*?)</span>[\s\S]*?class="xiaoquInfoContent">(.*?)</span>[\s\S]*?class="xiaoquInfoContent">(.*?)</span>'\
                   + r'[\s\S]*?class="xiaoquInfoContent">(.*?)</span>[\s\S]*?class="xiaoquInfoContent">(.*?)</span>[\s\S]*?class="xiaoquInfoContent">[\s\S]*?<span mendian="(.*?)" xiaoqu="[\s\S]*?</span>[\s\S]*?</h3><a href="http://cs.lianjia.com/ershoufang/(.*?)/[\s\S]*?<div class="mainContent"><div class="title">小区均价：(.*?)<span>']

            xiaoqu = re_fuc(cont, rel, 'xiaoqu')

            print (xiaoqu)
            print ("----")
            key = dict()
            key['url'] = url
            key[u'小区名称'] = xiaoqu[0][0]
            key[u'小区地址'] = xiaoqu[0][1]
            key[u'城市'] = xiaoqu[0][2]
            key[u'区'] = xiaoqu[0][3]
            key[u'道路'] = xiaoqu[0][4]
            key[u'建成时间'] = xiaoqu[0][5]
            key[u'建筑类型'] = xiaoqu[0][6]
            key[u'物业费'] = xiaoqu[0][7]
            key[u'物业公司'] = xiaoqu[0    ][8]
            key[u'开发商'] = xiaoqu[0][9]
            key[u'容积率/绿化率'] = xiaoqu[0][10]
            key[u'楼栋总数'] = xiaoqu[0][11]
            key[u'房屋总数'] = xiaoqu[0][12]
            key[u'小区经纬度'] = xiaoqu[0][13]
            key[u'小区唯一标识符'] = xiaoqu[0][14]
            key[u'小区均价'] = xiaoqu[0][15]
            tab2.insert(key)
            print u'插入成功！'
            time.sleep(1)
        else:
            print u'已爬取过此小区，无需再次爬取。'
