# _*_coding:utf-8_*_
import json
import requests
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

client = MongoClient()
dbName = 'lianjia'
dbTable = 'xiaoqu'
tab = client[dbName][dbTable]
dbTable2 = 'xiaoqu_price'
tab2 = client[dbName][dbTable2]

ses = requests.session()
ses.get('http://cs.lianjia.com/xiaoqu/rs/')

xiaoqus = tab.find()
for x in xiaoqus:
    xiaoqu = x['xiaoqu']
    id = x['url'].split('/')[-2]
    url = 'http://cs.lianjia.com/fangjia/priceTrend/c%s'%id
    print url
    print xiaoqu
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

    merge = tab2.find_one({'url' : url})
    if not merge:
        html = ses.post(url, headers = headers)
        cont = html.text
        if cont:
            price = json.loads(cont)
            if price['currentLevel']:
                price_all = price['upLevel']['dealPrice']['total']
                months = price['upLevel']['month']
                key = dict()
                for i in xrange(len(price_all)):
                    key[months[i]] = price_all[i]

                key['url'] = url
                key[u'小区'] = xiaoqu
                tab2.insert(key)
                print '插入成功！'
    else:
        print '已爬取过该小区，无需重复抓取。'
