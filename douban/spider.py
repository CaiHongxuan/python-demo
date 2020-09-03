# -*- coding: utf-8 -*-
# @Author: 17586
# @Date: 2020/8/17 20:59

from urllib import request, error
from bs4 import BeautifulSoup
import xlwt
import re
import sqlite3


def main():
    base_url = 'https://movie.douban.com/top250'
    save_path_excel = '.\\豆瓣电影Top250.xls'
    save_path_sqlite = '.\\douban.db'

    # 获取并解析数据
    print('开始爬取豆瓣电影TOP250。。。')
    data = get_data(base_url)

    # 保存数据
    print('保存数据。。。')
    # save_data_to_excel(data, save_path_excel)
    save_data_to_sqlite(data, save_path_sqlite)
    print('爬取结束')


# 获取数据
def get_data(base_url):
    findlink = re.compile(r'<a.*href="(.*?)">', re.S)
    findimg = re.compile(r'<img.*src="(.*?)"', re.S)
    findtitle = re.compile(r'<span.*class="title">(.*)</span>')
    findbd = re.compile(r'<p.*class="">\s*(.*?)\s*</p>', re.S)
    findrating = re.compile(r'<span.*class="rating_num" property="v:average">(.*?)</span>', re.S)
    findjudge = re.compile(r'<span>(\d*)人评价</span>')
    findinq = re.compile(r'<span.*class="inq">(.*)</span>', re.S)
    datalist = []
    for i in range(0, 10):
        print('爬取第 %d 页数据。。。' % (i + 1))
        url = base_url + "?start=" + str(i*25)
        html = ask_url(url)
        bs = BeautifulSoup(html, 'html.parser')
        for item in bs.find_all('div', class_="item"):
            data = []
            item = str(item)
            # 电影详情链接
            movielink = re.findall(findlink, item)[0]
            data.append(movielink)

            # 电影图片
            movieimg = re.findall(findimg, item)[0]
            data.append(movieimg)

            # 电影名称
            movietitle = re.findall(findtitle, item)
            if len(movietitle) == 2:
                data.append(movietitle[0])  # 中文名
                otitle = movietitle[1].strip('\n\t\r\xa0/')  # 外文名
                data.append(otitle)
            else:
                data.append(movietitle[0])
                data.append('')

            # 概况
            moviebd = re.findall(findbd, item)[0]
            moviebd = re.sub(r'<br(\s+)?/>(\s+)?', ' ', moviebd)
            data.append(moviebd)

            # 评价人数
            moviejudge = re.findall(findjudge, item)[0]
            data.append(moviejudge)

            # 评分
            movierating = re.findall(findrating, item)[0]
            data.append(movierating)

            # 评价
            movieinq = ''
            if len(re.findall(findinq, item)) > 0:
                movieinq = re.findall(findinq, item)[0]
            data.append(movieinq)

            datalist.append(data)
        print('第 %d 页数据爬取完成' % (i + 1))
    return datalist


# 获取指定url的网页数据
def ask_url(url):
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'
    }
    req = request.Request(url, headers=head)
    html = ''
    try:
        response = request.urlopen(req)
        html = response.read().decode('utf-8')
    except error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    except Exception as e:
        print(e)
    return html


# 保存数据到Excel
def save_data_to_excel(data, save_path):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('豆瓣电影TOP250', cell_overwrite_ok=True)
    head_col = ['电影详情链接', '电影图片', '影片中文名', '影片外文名', '概况', '评价人数', '评分', '评价']
    for i in range(len(head_col)):
        sheet.write(0, i, head_col[i])

    for i in range(len(data)):
        for j in range(len(data[i])):
            sheet.write(i + 1, j, data[i][j])
    book.save(save_path)


# 保存数据到sqlite
def save_data_to_sqlite(data, save_path):

    try:
        init_db(save_path)
        conn = sqlite3.connect(save_path)
        cur = conn.cursor()

        for i in range(len(data)):
            for j in range(len(data[i])):
                if j == 5 or j == 6:
                    continue
                data[i][j] = '"' + data[i][j] + '"'
            sql = '''
                insert into movies(`link_url`, `img_url`, `cname`, `fname`, `summary`, `judge_num`, `rate`, `inq`) 
                values (%s)
            ''' % (",".join(data[i]))
            cur.execute(sql)

        conn.commit()
        cur.close()
        conn.close()
    except sqlite3.DatabaseError as e:
        print(e)
    except Exception as e:
        print(e)


# 创建保存电影信息的表
def init_db(save_path):
    conn = sqlite3.connect(save_path)
    cur = conn.cursor()

    sql = '''
        create table movies(
        id integer primary key autoincrement,
        link_url varchar,
        img_url varchar,
        cname varchar,
        fname varchar,
        summary text,
        judge_num integer default 0,
        rate float default 0,
        inq text
        )
    '''
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
