# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: book.py
@time: 2023/3/9 20:50
"""

import os
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

"""
小说采集
起点中文网
    完结 + (人气、收藏、字数、推荐)
    书名 + 作者 + 字数 + 粉丝
    url: https://www.qidian.com/finish/orderId11/
         https://m.qidian.com/book/1004608738.html?source=pc_jump
    
QQ阅读
    完结 + (人气、收藏)
    书名 + 作者 + 粉丝 + 评分
    url: https://book.qq.com/book-cate/0-0-2-0-0-0-1-1
         https://ubook.reader.qq.com/book-detail/660366?q_f=4000001
    
番茄小说
    完结 + (人气、字数)
    书名 + 作者 + 字数 + 粉丝
    url: https://fanqienovel.com/library/stat0/page_1?sort=hottes
    
"""


class BaseSpider:
    """
    爬虫基类
    """
    def __init__(self):
        self.BASE_DIR = os.path.dirname(__file__)
        self.session = requests.session()

    @staticmethod
    def get_random_user_agent():
        """获取随机请求头"""
        return UserAgent().random

    def get_headers(self, accept, host, refer):
        """请求头封装"""
        headers = {
            "Accept": accept,
            "Host": host,
            "Referer": refer,
            "User-Agent": self.get_random_user_agent(),
        }
        return headers

    def get_html(self, url):
        """
        :param url: 初始化地址，返回html
        :return:
        """
        return self.session.get(url=url, timeout=3).text

    @staticmethod
    def get_type_url_list():
        pass

    @staticmethod
    def parse_html_by_bs4(html):
        """
        bs4解析html
        :param html:
        :return: 将小说详情链接写入json文件
        """
        soup = BeautifulSoup(html, "html.parser")

    def dict_init(self):
        """
        目录初始化
        :return:
        """
        pass

    def run(self):
        """
        程序入口
        :return:
        """
        pass


class QiDianSpider(BaseSpider):
    """
    起点爬虫
    1. 获取每个分类地址
        1.1 获取下一页数据
        1.2 将所有小说地址存在一个列表
    2. 遍历该分类下小说列表
        2.1 解析存储
    """
    def __init__(self):
        super(QiDianSpider, self).__init__()

    @staticmethod
    def get_type_url_list():
        """
        返回各个种类的URL列表: 5页
        人气榜: https://www.qidian.com/finish/page1/
        收藏榜: https://www.qidian.com/finish/orderId11-page1/
        字数榜: https://www.qidian.com/finish/orderId3-page2/
        推荐榜: https://www.qidian.com/finish/orderId2-page3/
        :return:
        """

        return {
            "人气榜": "https://www.qidian.com/finish/page%s/",
            "收藏榜": "https://www.qidian.com/finish/orderId11-page%s/",
            "字数榜": "https://www.qidian.com/finish/orderId3-page%s/",
            "推荐榜": "https://www.qidian.com/finish/orderId2-page%s/"
        }


class QQSpider(BaseSpider):
    """QQ阅读爬虫"""
    def __init__(self):
        super(QQSpider, self).__init__()

    @staticmethod
    def get_type_url_list():
        """
        返回各个种类的URL列表: 50页
        人气榜: https://book.qq.com/book-cate/0-0-2-0-0-0-0-1
        收藏榜: https://book.qq.com/book-cate/0-0-2-0-0-0-1-1
        :return:
        """
        return {
            "人气榜": "https://book.qq.com/book-cate/0-0-2-0-0-0-0-%s",
            "收藏榜": "https://book.qq.com/book-cate/0-0-2-0-0-0-1-%s"
        }


class TomatoSpider(BaseSpider):
    """番茄爬虫"""
    def __init__(self):
        super(TomatoSpider, self).__init__()

    @staticmethod
    def get_type_url_list():
        """
        返回各个种类的URL列表: 6页
        人气榜: https://fanqienovel.com/library/stat0/page_3?sort=hottes
        字数榜: https://fanqienovel.com/library/stat0/page_5?sort=count
        :return:
        """
        return {
            "人气榜": "https://fanqienovel.com/library/stat0/page_%s?sort=hottes",
            "字数榜": "https://fanqienovel.com/library/stat0/page_%s?sort=count"
        }


if __name__ == '__main__':
    pass
