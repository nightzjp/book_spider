# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: book.py
@time: 2023/3/9 20:50
"""

import os
import json
import time

import xlsxwriter
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

    def get_html(self, url, headers):
        """
        :param url: 初始化地址，返回html
        :param headers 请求头
        :return:
        """
        return self.session.get(url=url, headers=headers, timeout=3).text

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
        return BeautifulSoup(html, "html.parser")

    def page_init(self, filename, page_start, page_end):
        """
        将初始化页码数据存入json
        :return:
        """
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                page_dict = json.loads(f.read())
                return page_dict
        url_list = self.get_type_url_list()
        if isinstance(url_list, dict):
            page_dict = []
            for key, value in url_list.items():
                page_dict.append(
                    {"type": key, "page_list": [value % page for page in range(page_start, page_end)]}
                )
            with open(filename, "w", encoding="utf-8") as f:
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

    def __init__(self, dirname="qidian"):
        super(QiDianSpider, self).__init__()
        self.dirname = dirname
        self.TD = os.path.join(self.DATE_DIR, self.dirname)
        if not os.path.exists(self.TD):
            os.mkdir(self.TD)
        self.EXCEL_PATH = os.path.join(self.TD, "excel")
        if not os.path.exists(self.EXCEL_PATH):
            os.mkdir(self.EXCEL_PATH)

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
        filename = os.path.join(self.TD, filename)
        return super().page_init(filename, page_start, page_end)

    def book_init(self, page_list, headers):
        """书籍详情初始化"""
        for item in page_list:
            filename = os.path.join(self.TD, item["type"] + ".json")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    book_list = json.loads(f.read())
                    yield item["type"], book_list
                    continue
            url_list = item["page_list"]  # 分页数据
            book_url_list = []  # 存储当前分类下所有书籍url
            for url in url_list:  # 获取每个分页
                soup = self.parse_html_by_bs4(self.get_html(url=url, headers=headers))
                item_list = soup.find_all("div", attrs={"class": "book-img-box"})
                for i in item_list:  # 获取分页详情列表
                    book_title = i.find("img").get("alt")
                    book_url = i.find("a").get("href").rsplit("/", 2)[1]
                    book_url_list.append({
                        "book_title": book_title.replace("在线阅读", ""),
                        "book_url": f"https://m.qidian.com/book/{book_url}.html?source=pc_jump"
                    })
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(book_url_list, indent=4, ensure_ascii=False))
                yield item["type"], book_url_list
                continue

    def run(self):
        """起点爬虫入口"""

        # 页码json初始化
        page_list = self.page_init(filename="qidian.json", page_start=1, page_end=6)

        # 请求头初始化
        headers = self.get_headers(
            accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            host="m.qidian.com",
            refer="https://m.qidian.com"
        )

        book = self.book_init(page_list, headers)
        for item in book:
            filename = item[0]
            book_list = item[1]
            workbook = xlsxwriter.Workbook(os.path.join(self.EXCEL_PATH, ".".join([filename, "xlsx"])))
            worksheet = workbook.add_worksheet()
            index = 0
            titles = ["书名", "作者", "字数", "粉丝"]
            for title in titles:
                worksheet.write(0, index, title)
                index += 1
            row = 1
            for i in book_list:
                try:
                    soup = self.parse_html_by_bs4(self.get_html(i["book_url"], headers=headers))
                    book_name = soup.find("h2", attrs={"class": "detail__header-detail__title"}).text
                    book_author = soup.find("h4", attrs={"class": "book-title"}).text
                    book_count = soup.find_all("p", attrs={"class": "detail__header-detail__line"})[1].text
                    book_fansi = soup.find("p", attrs={"class": "digital-main"}).find("span").text
                    print(book_name, book_author, book_count, book_fansi)
                    worksheet.write(row, 0, book_name)
                    worksheet.write(row, 1, book_author)
                    worksheet.write(row, 2, book_count)
                    worksheet.write(row, 3, book_fansi)
                except Exception as e:
                    print(e)
                    time.sleep(1)
                    continue
                finally:
                    row += 1
            workbook.close()


class QQSpider(BaseSpider):
    """QQ阅读爬虫"""

    def __init__(self, dirname="qq"):
        super(QQSpider, self).__init__()
        self.dirname = dirname
        self.TD = os.path.join(self.DATE_DIR, self.dirname)
        if not os.path.exists(self.TD):
            os.mkdir(self.TD)
        self.EXCEL_PATH = os.path.join(self.TD, "excel")
        if not os.path.exists(self.EXCEL_PATH):
            os.mkdir(self.EXCEL_PATH)

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
        filename = os.path.join(self.TD, filename)
        return super().page_init(filename, page_start, page_end)

    def book_init(self, page_list, headers):
        """书籍详情初始化"""
        for item in page_list:
            filename = os.path.join(self.TD, item["type"] + ".json")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    book_list = json.loads(f.read())
                    yield item["type"], book_list
                    continue
            url_list = item["page_list"]
            book_url_list = []
            for url in url_list:
                soup = self.parse_html_by_bs4(self.get_html(url=url, headers=headers))
                item_list = soup.find_all("div", attrs={"class": "book-large rank-book"})
                for i in item_list:
                    book_title = i.find("a").get("title")
                    book_url = i.find("a").get("href").rsplit("/", 1)[1]
                    book_url_list.append({
                        "book_title": book_title,
                        "book_url": f"https://ubook.reader.qq.com/book-detail/{book_url}?q_f=4000001"
                    })
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(book_url_list, indent=4, ensure_ascii=False))
                yield item["type"], book_url_list
                continue

    def run(self):
        """QQ阅读爬虫入口"""
        page_list = self.page_init(filename="qq.json", page_start=1, page_end=51)

        headers = self.get_headers(
            accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            host="ubook.reader.qq.com",
            refer="https://ubook.reader.qq.com/"
        )
        book = self.book_init(page_list, headers)
        for item in book:
            filename = item[0]
            book_list = item[1]
            workbook = xlsxwriter.Workbook(os.path.join(self.EXCEL_PATH, ".".join([filename, "xlsx"])))
            worksheet = workbook.add_worksheet()
            index = 0
            titles = ["书名", "作者", "字数", "评分"]
            for title in titles:
                worksheet.write(0, index, title)
                index += 1
            row = 1
            for i in book_list:
                try:
                    soup = self.parse_html_by_bs4(self.get_html(url=i["book_url"], headers=headers))
                    book_name = soup.find("h2", attrs={"class": "detail-x__header-detail__title"}).text
                    book_author = soup.find("a", attrs={"class": "detail-x__header-detail__author"}).text
                    book_count = soup.find("p", attrs={"class": "detail-x__header-detail__line"}).text
                    book_rate = soup.find("span", attrs={"class": "detail-x__header-detail__score"}).text
                    print(row, book_name.replace(" ", ""), book_author.replace(" ", ""), book_count.replace(" ", "").split("·")[1], book_rate)
                    worksheet.write(row, 0, book_name.replace(" ", ""))
                    worksheet.write(row, 1, book_author.replace(" ", ""))
                    worksheet.write(row, 2, book_count.replace(" ", "").split("·")[1])
                    worksheet.write(row, 3, book_rate)
                except Exception as e:
                    print(e)
                    time.sleep(1)
                    continue
                finally:
                    row += 1
            workbook.close()


class TomatoSpider(BaseSpider):
    """番茄爬虫"""

    def __init__(self, dirname="tomato"):
        super(TomatoSpider, self).__init__()
        self.dirname = dirname
        self.TD = os.path.join(self.DATE_DIR, self.dirname)
        if not os.path.exists(self.TD):
            os.mkdir(self.TD)
        self.EXCEL_PATH = os.path.join(self.TD, "excel")
        if not os.path.exists(self.EXCEL_PATH):
            os.mkdir(self.EXCEL_PATH)

    @staticmethod
    def get_type_url_list():
        """
        返回各个种类的URL列表: 6页
        人气榜: https://fanqienovel.com/library/stat0/page_3?sort=hottes
        字数榜: https://fanqienovel.com/library/stat0/page_5?sort=count
        :return:
        """
        return {
            "人气榜": "https://fanqienovel.com/api/author/library/book_list/v0/?page_count=18&page_index=%s&gender=-1&category_id=-1&creation_status=0&word_count=-1&sort=0",
            "字数榜": "https://fanqienovel.com/api/author/library/book_list/v0/?page_count=18&page_index=%s&gender=-1&category_id=-1&creation_status=0&word_count=-1&sort=2"
        }

    def page_init(self, filename, page_start, page_end):
        filename = os.path.join(self.TD, filename)
        return super().page_init(filename, page_start, page_end)

    def book_init(self, page_list, headers):
        """书籍详情初始化"""
        for item in page_list:
            filename = os.path.join(self.TD, item["type"] + ".json")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    book_list = json.loads(f.read())
                    yield item["type"], book_list
                    continue
            url_list = item["page_list"]
            book_url_list = []
            for url in url_list:
                res_json = json.loads(self.get_html(url=url, headers=headers))
                for i in res_json["data"]["book_list"]:
                    book_title = str(i["book_name"])
                    book_url = i["book_id"]
                    book_url_list.append({
                        "book_title": book_title,
                        "book_url": f"https://fanqienovel.com/page/{book_url}?enter_from=stack-room"
                    })
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(book_url_list, indent=4, ensure_ascii=False))
                yield item["type"], book_url_list
                continue

    def run(self):
        """番茄爬虫入口"""
        page_list = self.page_init(filename="tomato.json", page_start=0, page_end=6)

        headers = self.get_headers(
            accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            host="fanqienovel.com",
            refer="https://fanqienovel.com/"
        )
        book = self.book_init(page_list, headers)
        for item in book:
            filename = item[0]
            book_list = item[1]
            workbook = xlsxwriter.Workbook(os.path.join(self.EXCEL_PATH, ".".join([filename, "xlsx"])))
            worksheet = workbook.add_worksheet()
            index = 0
            titles = ["书名", "作者", "字数", "粉丝"]
            for title in titles:
                worksheet.write(0, index, title)
                index += 1
            row = 1
            for i in book_list:
                try:
                    soup = self.parse_html_by_bs4(self.get_html(url=i["book_url"], headers=headers))
                    book_name = soup.find("div", attrs={"class": "info-name"}).find("h1").text
                    book_author = soup.find("div", attrs={"class": "author-name"}).find("span", attrs={
                        "class": "author-name-text"}).text
                    book_count = soup.find("div", attrs={"class": "info-count-word"}).text
                    book_fansi = soup.find("div", attrs={"class": "info-count-read"}).text
                    print(book_name, book_author, book_count, book_fansi)
                    worksheet.write(row, 0, book_name)
                    worksheet.write(row, 1, book_author)
                    worksheet.write(row, 2, book_count)
                    worksheet.write(row, 3, book_fansi)

                except Exception as e:
                    print(e)
                    time.sleep(1)
                    continue
                finally:
                    row += 1

            workbook.close()


if __name__ == '__main__':
    def run(tp):
        if tp == "qd":
            print("起点小说采集")
            qd = QiDianSpider()
            qd.run()
        elif tp == "qq":
            print("QQ阅读小说采集")
            qq = QQSpider()
            qq.run()
        elif tp == "t":
            print("番茄小说采集")
            t = TomatoSpider()
            t.run()
        else:
            print("未知")
