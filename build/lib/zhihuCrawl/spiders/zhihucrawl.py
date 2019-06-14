# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
from ..items import  UserInfoItem,RelationItem
import  json

class ZhihucrawlSpider(scrapy.Spider):
    name = 'zhihucrawl'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/people/xing-er-xiong']


    def parse(self, response):

        user_id = str.split(response.url,'/')[-1]
        user_image_url = response.xpath(".//img[@class='Avatar Avatar--large UserAvatar-inner']/@src").extract_first()
        name = response.xpath(".//h1[@class='ProfileHeader-title']/span/text()").extract_first()
        info = response.xpath(".//div[@class='ProfileHeader-infoItem'][1]/text()").extract()
        business = ''
        position = ''
        if len(info) > 1:
            business = info[0]
            position = info[-1]
        elif len(info) == 1:
            business = info[0]
        education = response.xpath(".//div[@class='ProfileHeader-infoItem'][2]/text()").extract()
        if len(education) ==0:
            education = ''
        sex = response.xpath(".//div[@class='ProfileHeader-iconWrapper']/svg/@class").extract()[-1]

        if sex and  u'female' in sex:
            gender = 'female'
        elif sex and 'male' in sex:
            gender = 'male'
        else:
            gender = ''
        followees_num = response.xpath(".//strong[@class='NumberBoard-itemValue']/text()").extract()[0]
        followers_num = response.xpath(".//strong[@class='NumberBoard-itemValue']/text()").extract()[-1]
        user_info_item = UserInfoItem(user_id=user_id,user_image_url=user_image_url,name=name,business=business,gender=gender,position=position,
                                      education=education,followees_num=followees_num,followers_num=followers_num)
        yield user_info_item

        followees = int(followees_num)
        followers = int(followers_num)

        params = {
            'include': 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics',
            'offset': 0,
            'limit': 20
        }

        if followees_num == 0:
            yield RelationItem(user_id=user_id,relation_type='followees',relations_id='')
        else:
            url = 'https://www.zhihu.com/api/v4/members/'+user_id+'/'+'followees?'

            num = 0
            while num < followees:
                params['offset'] = num
                followees_url = url+urlencode(params)
                num +=20
                yield scrapy.Request(url=followees_url, meta={'user_id': user_id, 'relation_type': 'followees'},
                                     callback=self.pare_relation)



        if followers == 0:
            yield RelationItem(user_id=user_id,relation_type='followers',relations_id='')
        else:
            url='https://www.zhihu.com/api/v4/members/'+user_id+'/'+'followers?'
            num = 0
            while num < followers:
                params['offset'] = num
                followees_url = url+urlencode(params)
                num +=20
                yield scrapy.Request(url=followees_url,meta={'user_id':user_id,'relation_type':'followers'},callback=self.pare_relation)


    def get_url(self,offset,url):
        '''
        获取我的关注或关注者json数据
        :param offset: 偏移量
        :param url: 初始url
        :param get_type: 类型
        :return:
        '''
        params = {
            'include': 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics',
            'offset': offset,
            'limit': 20
        }
        return url+urlencode(params)

    def pare_relation(self, response):
        relation_id =[]
        user_id = response.meta['user_id']
        relation_type = response.meta['relation_type']
        relations_json = json.loads(response.text)
        relations_items = relations_json.get('data')
        if relations_items:
            for item in relations_items:
                id = item.get('url_token')
                relation_id.append(id)
                id_url = 'https://www.zhihu.com/people/'+id
                print(id_url)
                #yield scrapy.Request(url=id_url,callback=self.parse)

        yield RelationItem(user_id=user_id,relation_type=relation_type,relations_id=relation_id)