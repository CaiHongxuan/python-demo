from flask import Flask, request, render_template
import sqlite3
import math

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


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
    return render_template('wordcloud.html')


@app.route('/team')
def team():
    return render_template('team.html')


if __name__ == '__main__':
    app.run(debug=True)
