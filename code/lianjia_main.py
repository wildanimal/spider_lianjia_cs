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

main_url = 'http://cs.lianjia.com/xiaoqu/rs/'
cont = getresp(main_url)

rel = [r'<div class="info"><div class="title"><a href="(.*?)" target="_blank" data-bl="list" data-log_index=".*?data-el="xiaoqu">(.*?)</a>']
xiaoqu = re_fuc(cont, rel, 'choice_route')
for x in xiaoqu:
    key = {'xiaoqu':x[1], 'url':x[0]}
    tab.insert(key)
print '第1页爬取成功！'

for i in xrange(2, 82, 1):
    print '开始爬取第%s页'%(str(i))
    main_url= 'http://cs.lianjia.com/xiaoqu/pg%s/'%(str(i))
    cont = getresp(main_url)
    rel = [r'<div class="info"><div class="title"><a href="(.*?)" target="_blank" data-bl="list" data-log_index=".*?data-el="xiaoqu">(.*?)</a>']
    xiaoqu = re_fuc(cont, rel, 'choice_route')
    for x in xiaoqu:
        #print x[0],x[1]
        key = {'xiaoqu':x[1], 'url':x[0]}
        tab.insert(key)
    print '第%s页爬取成功！' % (str(i))
    time.sleep(1)
