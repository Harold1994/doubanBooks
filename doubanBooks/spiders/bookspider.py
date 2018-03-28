# -*- coding: utf-8 -*-
import urllib

import scrapy
from PIL import Image
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from doubanBooks.items import DoubanbooksItem


class BookspiderSpider(CrawlSpider):
    name = 'bookspider'
    allowed_domains = ['douban.com']
    start_urls = ["https://book.douban.com/tag/"]
    rules = (
        Rule(LinkExtractor(allow=r'tag/.{2,4}'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'https://book.douban.com/tag/.+/?start=\d+&type=T'), callback='parse_item2', follow=True),
        # Rule(LinkExtractor(allow=r'https://book.douban.com/subject/\d+/'), callback='parse_item2',follow=False),
        # Rule(LinkExtractor(allow=r'https://book.douban.com/subject/\d/reviews'), callback='parse_item3', follow=False),
    )




    # def start_requests(self):
    #     '''
    #     重写start_requests，请求登录页面
    #     '''
    #     return [scrapy.FormRequest("https://accounts.douban.com/login", meta={"cookiejar": 1},
    #                                callback=self.parse_before_login)]
    #


    def parse_item0(self, response):
        sel = Selector(response);
        # item['book_tag'] = sel.xpath('/html/body/div[3]/div[1]/h1/text()').extract()[0].split(':')[1].strip()

    def parse_item(self, response):
        pass
       # print(response)

    def parse_item2(self, response):
        sel = Selector(response)
        item = DoubanbooksItem()
        item['book_tag'] = sel.xpath('/html/body/div[3]/div[1]/h1/text()').extract()[0].strip().split(':')[1]
        book_list = sel.css('#subject_list > ul > li')
        for book in book_list:

            try:
                # strip() 方法用于移除字符串头尾指定的字符（默认为空格）
                item['book_name'] = book.xpath('div[@class="info"]/h2/a/text()').extract()[0].strip()
                item['book_star'] = book.xpath("div[@class='info']/div[2]/span[@class='rating_nums']/text()").extract()[0].strip()
                item['book_pl'] = book.xpath("div[@class='info']/div[2]/span[@class='pl']/text()").extract()[0].strip()
                item['book_desc'] = book.xpath("div[2]/p/text()").extract()[0]
                item['book_id'] = book.xpath('div[@class="info"]/h2[@class=""]/a/@href').extract()[0].strip().split('/')[-2]
                pub = book.xpath('div[@class="info"]/div[@class="pub"]/text()').extract()[0].strip().split('/')
                item['book_price'] = pub.pop()
                item['book_date'] = pub.pop()
                item['book_publish'] = pub.pop()
                item['book_author'] = '/'.join(pub)

                yield item
            except:
                pass

# def parse_item4(self, response):
#         sel = Selector(response);
#         item = DoubanbooksItem()
#         item['user_name'] = sel.xpath('div[@class="aside"]/div[@class="sidebar-info-wrapper"]/div[2]/a/text()').extract()[0].strip()
#         item['user_score'] = sel.xpath('div[@class="aside"]/div[@class="sidebar-info-wrapper"]/div[2]/a/text()').extract()[0].strip()
#         yield item

    def parse_before_login(self, response):
        print("登录前表单填充")
        captcha_id = response.xpath('//input[@name="captcha-id"]/@value').extract_first()
        captcha_image_url = response.xpath('//img[@id="captcha_image"]/@src').extract_first()
        if captcha_image_url is None:
            print("登录时无验证码")
            formdata = {
                "form_email": "18911341910",
                # 请填写你的密码
                "form_password": "lh1994114",
                "login": "登录",
                "redir": "https://www.douban.com/",
                "source": "index_nav",
            }
        else:
            print("登录时有验证码")
            save_image_path = "/media/harold/SpareDisk/pythonProject/captcha.jpeg"
            # 将图片验证码下载到本地
            urllib.request.urlretrieve(captcha_image_url, save_image_path)
            # 打开图片，以便我们识别图中验证码
            try:
                im = Image.open(save_image_path)
                im.show()
            except:
                pass
            # 手动输入验证码
            captcha_solution = input('根据打开的图片输入验证码:')
            formdata = {
                "source": "None",
                "redir": "https://www.douban.com/",
                "form_email": "13227708059@163.com",
                # 此处请填写密码
                "form_password": "lh1994114",
                "captcha-solution": captcha_solution,
                "captcha-id": captcha_id,
                "login": "登录",
            }

        print("登录中")
        # 提交表单
        return scrapy.FormRequest.from_response(response, meta={"cookiejar": response.meta["cookiejar"]},
                                                formdata=formdata,
                                                callback=self.parse_after_login)


    def parse_after_login(self, response):
        '''
        验证登录是否成功
        '''
        account = response.xpath('/html/body/div[1]/div/div[1]/ul/li[2]/a/span[1]').extract_first()
        print(account)
        if account is None:
            print("登录失败")
        else:
            print(u"登录成功,当前账户为 %s" % account)
            yield self.make_requests_from_url("https://book.douban.com/tag/")

