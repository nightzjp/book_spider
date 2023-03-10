# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: book.py
@time: 2023/3/9 20:50
"""

import os
import json
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
        self.DATE_DIR = os.path.join(self.BASE_DIR, "data")
        self.session = requests.session()
        if not os.path.exists(self.DATE_DIR):
            os.mkdir(self.DATE_DIR)

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

    def page_init(self, filename, page_start, page_end):
        """
        将初始化页码数据存入json
        :return:
        """
        file_name = os.path.join(self.DATE_DIR, filename)
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                page_dict = json.loads(f.read())
                return page_dict
        url_list = self.get_type_url_list()
        if isinstance(url_list, dict):
            page_dict = []
            for key, value in url_list.items():
                page_dict.append(
                    {"type": key, "page_list": [value % page for page in range(page_start, page_end)]}
                )
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(json.dumps(page_dict, indent=4, ensure_ascii=False))
                return page_dict

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

    def page_init(self, filename, page_start, page_end):
        """初始化起点json文件"""
        return super().page_init(filename, page_start, page_end)

    def run(self):
        """起点爬虫入口"""

        # 页码json初始化
        self.page_init(filename="qidian.json", page_start=1, page_end=6)


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

    def page_init(self, filename, page_start, page_end):
        """初始化QQ阅读json文件"""
        return super().page_init(filename, page_start, page_end)

    def run(self):
        """QQ阅读爬虫入口"""
        self.page_init(filename="qq.json", page_start=1, page_end=51)


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

    def page_init(self, filename, page_start, page_end):
        return super().page_init(filename, page_start, page_end)

    def run(self):
        """番茄爬虫入口"""
        self.page_init(filename="tomato.json", page_start=1, page_end=7)


if __name__ == '__main__':
    # 起点
    # qd = QiDianSpider()
    # qd.run()

    # QQ阅读
    # qq = QQSpider()
    # qq.run()

    # 番茄
    # t = TomatoSpider()
    # t.run()
    pass
