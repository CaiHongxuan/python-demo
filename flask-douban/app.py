from flask import Flask, request, render_template
from wordcloud import WordCloud  # 词云
import matplotlib.pyplot as plt  # 绘图，数据可视化
from PIL import Image  # 图片处理
import numpy as np  # 矩阵运算
import sqlite3
import math
import jieba  # 分词

app = Flask(__name__)


@app.route('/')
def index():
    conn = sqlite3.connect('./douban.db')
    cur = conn.cursor()
    sql = 'select judge_num,inq from movies'
    data = cur.execute(sql)
    text = ""
    num = 0
    for item in data:
        num = num + item[0]
        text = text + item[1]
    conn.commit()
    cur.close()
    conn.close()

    cut = jieba.cut(text)
    string = " ".join(cut)
    word_count = len(string)  # 词云数
    num = '%.2f' % (num / 100000000)  # 评分总人数
    return render_template('index.html', total=250, word_count=word_count, num=num)


@app.route('/movies')
def movies():
    per_page = 10
    page = int(request.args.get('page', '1'))
    offset = (page - 1) * per_page
    movies = []
    conn = sqlite3.connect('./douban.db')
    cur1 = conn.cursor()
    cur2 = conn.cursor()
    sql = 'select * from movies limit %s, %s' % (offset, per_page)
    count_sql = 'select count(id) from movies'
    data = cur1.execute(sql)
    count = cur2.execute(count_sql)
    for item in data:
        movies.append(item)
    total = count.fetchone()
    total = math.ceil(total[0] / per_page)
    conn.commit()
    cur1.close()
    cur2.close()
    conn.close()
    return render_template('movies.html', movies=movies, current_page=page, total=total)


@app.route('/score')
def score():
    num = []
    rate = []
    conn = sqlite3.connect('./douban.db')
    cur = conn.cursor()
    sql = 'select count(*),rate from movies group by rate'
    data = cur.execute(sql)
    for item in data:
        num.append(item[0])
        rate.append(item[1])
    conn.commit()
    cur.close()
    conn.close()
    return render_template('score.html', num=num, rate=rate)


@app.route('/wordcloud')
def wordcloud():
    # conn = sqlite3.connect('./douban.db')
    # cur = conn.cursor()
    # sql = 'select inq from movies'
    # data = cur.execute(sql)
    # text = ""
    # for item in data:
    #     text = text + item[0]
    # conn.commit()
    # cur.close()
    # conn.close()
    #
    # cut = jieba.cut(text)
    # string = " ".join(cut)
    #
    # img = Image.open(r'./static/assets/onepage/img/choose-us.png')
    # img_arr = np.array(img)  # 图片转数组
    #
    # wc = WordCloud(background_color='white', mask=img_arr, font_path="msyh.ttc").generate_from_text(string)
    #
    # # 绘图
    # plt.figure(1)
    # plt.imshow(wc)
    # plt.axis('off')
    # plt.savefig(r'./static/assets/onepage/img/wordcloud.png', dpi=500)

    return render_template('wordcloud.html')


@app.route('/team')
def team():
    return render_template('team.html')


if __name__ == '__main__':
    app.run(debug=True)
