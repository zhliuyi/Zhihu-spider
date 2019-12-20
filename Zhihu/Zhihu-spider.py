import requests
from lxml import etree
import pymongo
import hashlib
class Zhihu(object):
    #部分信息初始化
    def __init__(self):
        self.url = 'https://www.zhihu.com/api/v4/search_v3?'
        self.search_words = ['面试','实习','找工作','简历']
        # self.search_words = ['面试']
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'referer': 'https://www.zhihu.com/search?type=content&q=%E9%9D%A2%E8%AF%95',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }


        self.client = pymongo.MongoClient()
        self.db = self.client['zhihu']
        self.parse()
        self.proxies=requests.get('http://127.0.0.1:5000/get').text
    #从代理池获取代理
    def daili(self):
        response = requests.get('http://127.0.0.1:5000/get')
        # print(response.text)
        proxies={
            'http':response.text
        }
        return proxies
    #加密算法
    def get_md5(self, value):
        md5 = hashlib.md5()
        md5.update(value.encode('utf-8'))
        return md5.hexdigest()
    #写入mongo
    def write_to_mongo(self,data):
        hash_url = self.get_md5(data['question_url'])
        data['hash_url'] = hash_url
        self.db['zhihu'].update({'hash_url': data['hash_url']}, {'$set': data}, True)
        print(data)
    #请求接口获取接口信息
    def get_html(self,url,params):
        response = requests.get(url,headers=self.headers,params=params,proxies=self.daili())
        return response.json()
    #解析详细页面中，找到关注者，浏览者数量
    def parse_detail(self,data,answer,question):
        # print(data,question,answer)
        url = 'https://www.zhihu.com/question/{}/answer/{}'.format(question,answer)
        data['question_url'] = url
        response = requests.get(url,headers=self.headers,proxies=self.daili())
        text = response.text
        # print(text)
        text = etree.HTML(text)
        text = text.xpath('//strong[@class="NumberBoard-itemValue"]/text()')

        stars = text[0]
        liulan = text[-1]
        data['question_follow_num'] = stars
        data['question_view_num'] = liulan
        # print(data)
        self.write_to_mongo(data)
    #分析接口获取部分信息
    def parse_search_json(self,text,word):
        b=0
        for data in text['data']:

            # print(data)
            if data.get('object',None):
                data = data.get('object')
                if data.get('type',None):
                    # print(data)
                    if data['type'] == 'answer':
                        b = b + 1
                        data_dict = {}

                        data_dict['search_terms'] = word
                        data_dict['search_rank'] = b
                        data_dict['question_title'] = data['question']['name']
                        data_dict['question_top_answer_username'] = data['author']['name']
                        data_dict['question_top_answer_id'] = data['author']['id']
                        question = data['id']
                        answer = data['question']['id']
                        self.parse_detail(data_dict,question,answer)
                        # print(data_dict)
    #分页
    def parse_serach(self,word):

        for i in range(0,181,20):
            params = {
                'q': '{}'.format(word),
                'offset': str(i),
                'limit' : '20',
            }
            text = self.get_html(self.url,params)
            self.parse_search_json(text,word)
    #获取关键字
    def parse(self):
        for word in self.search_words:
            self.parse_serach(word)
if __name__ == '__main__':
    Zhihu()
