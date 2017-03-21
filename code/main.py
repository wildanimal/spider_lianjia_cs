# _*_coding:utf-8_*_
import time
import requests
from pub_fuc import re_fuc
from pymongo import MongoClient
import json, string,traceback
from bs4 import BeautifulSoup

import sys
import random

reload(sys)
sys.setdefaultencoding( "utf-8" )

client = MongoClient()
dbName = 'lianjia'
coll_xiaoqu = client[dbName]['cs_xiaoqu']
coll_price = client[dbName]['cs_price']

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

        #html.encoding = 'gbk'
        data = html.text.encode('iso8859-1').decode('utf-8')
    except Exception, what:
        traceback.print_exc()
    return data

main_url = 'http://cs.lianjia.com/xiaoqu/rs/'
first_page_content = getresp(main_url)
#print(cont)

# rel = [r'<div class="info">\s+<div class="title">\s+<a href="(.*?)" target="_blank">(.*?)</a>']
# xiaoqu = re_fuc(cont, rel, 'choice_route')
#print(xiaoqu)

listpage_soup = BeautifulSoup(first_page_content, "lxml")
page_box_tag = listpage_soup.find("div", {"class" : "page-box house-lst-page-box"})
total_page = 0
if page_box_tag:
    try:
        page_data = json.loads(page_box_tag.get("page-data"))
        print(page_data)
        total_page = page_data["totalPage"]
    except:
        traceback.print_exc()
        print("无法获取总页数，网站内容格式已改变，请修改！")
        sys.exit(1)

if not total_page :
    print("无法获取总页数，程序退出。")
    sys.exit(1)

wait_time = random.randint(10, 60)
print(u"等待%d秒抓取进行下一页小区信息抓取" % wait_time)
time.sleep(wait_time)

for i in xrange(1, total_page + 1, 1):
    print '开始爬取第%d页' % i
    main_url= 'http://cs.lianjia.com/xiaoqu/pg%d/'% i
    first_page_content = getresp(main_url)
    listpage_soup = BeautifulSoup(first_page_content, "lxml")
    xiaoqus = listpage_soup.find("ul", {"class" : "listContent"}).find_all("li")
    for xiaoqu in xiaoqus:
        tags_a = xiaoqu.find_all("a")
        print(u"开始抓取小区 '%s' 的信息 " % tags_a[1].string)
        # loc_arr = tags_a[2].get("xiaoqu").split(',')
        # lng = float(loc_arr[0][1:].strip())
        # lat = float(loc_arr[1].strip())
        xiaoqu_data = {
            "url" : tags_a[1].get("href"),
            "title" : tags_a[1].string,
            "district" : tags_a[4].string,
            "bizcircle" : tags_a[5].string,
            # "lng" : lng,
            # "lat" : lat,
        }
        xiaoqu_data["web_id"] = xiaoqu_data['url'].split('/')[-2]
        print(xiaoqu_data)

        wait_time = random.randint(10,60)
        print(u"等待%d秒抓取小区详细信息" % wait_time)
        time.sleep(wait_time)

        xiaoqu_info = getresp(xiaoqu_data["url"])
        house_info_soup = BeautifulSoup(first_page_content, "lxml")
        infoItems = house_info_soup.find_all("span", {"class" : "xiaoquInfoContent"})
        xiaoqu_data["year"] = infoItems[0].string
        xiaoqu_data["type"] = infoItems[1].string
        xiaoqu_data["manage_costs"] = infoItems[2].string
        xiaoqu_data["manage_company"] = infoItems[3].string
        xiaoqu_data["building_company"] = infoItems[4].string
        xiaoqu_data["building_count"] = infoItems[5].string
        xiaoqu_data["house_count"] = infoItems[6].string

        loc = infoItems[7].find("span").get("mendian").split(',')
        xiaoqu_data["lng"] = float(loc[0])
        xiaoqu_data["lat"] = float(loc[1])

        coll_xiaoqu.insert(xiaoqu_data)

        # 等待一段时间，以免被发现是爬虫
        wait_time = random.randint(10,60)
        print(u"等待%d秒抓取历史房价" % wait_time)
        time.sleep(wait_time)

        price_url = 'http://cs.lianjia.com/fangjia/priceTrend/c%s' % xiaoqu_data["web_id"]
        price_content = getresp(price_url)
        price = json.loads(price_content)
        if price['currentLevel']:
            price_all = price['upLevel']['dealPrice']['total']
            months = price['upLevel']['month']
            price_data = dict()
            for i in xrange(len(price_all)):
                price_data[months[i]] = price_all[i]

            price_data['url'] = price_url
            price_data[u'xiaoqu'] = id
            coll_price.insert(price_data)

        wait_time = random.randint(10,60)
        print(u"等待%d秒抓取进行下一个小区信息抓取" % wait_time)
        time.sleep(wait_time)
    #tab.insert(key)
