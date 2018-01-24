import sys, time, os, re, mysql.connector
dir_path = '/Users/twocoldtwo/Desktop/Project/Article/马克吐温'
config = {
            'user': 'root',
            'password': 'root',
            'port': 3306,
            'host': '127.0.0.1',
            'database': 'bruce'}

def get_text(file_name):
    with open('{di}/{fi}'.format(di = dir_path, fi = file_name), 'r') as f:
        ctt = f.read()
        ctt = ctt[ctt.find('\"y_article_content clearfix\">') + len('\"y_article_content clearfix\">'):ctt.find('$(\".y_s_content a\")')]
        ctt = ctt[ctt.find('收藏本文') + len('收藏本文'): ctt.find('版权')]
        ctt = ctt[ctt.find('<p class="description">') + len('<p class="description">'): ctt.find('楼主')]
        istop = sorted([ctt.rfind('。'), ctt.rfind('！'), ctt.rfind('）'), ctt.rfind('？')], reverse = True)[0]
        ctt = ctt[: istop + 1].replace('</p>', '\r\n').replace('\"', '\\"')
        ctt = re.subn(r'<(\S*?)[^>]*>|<.*?/>|[^<^>]*?>|[&nbsp;]|\{[\S\s]+?\}|\[[\S\s]+?\]', '', ctt)[0]
        return ctt

def get_items_of_dir(d_path):
    return os.listdir(d_path)

def db_select(id, col):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    sql = 'SELECT {col} FROM article WHERE id={id}'.format(col = col, id = id)
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0]

def db_update(id, title):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    sql = 'UPDATE article SET title="{title}" WHERE id={id}'.format(title = title, id = id)
    print(sql)
    print(cur.execute(sql))
    conn.commit()
    cur.close()
    conn.close()

def db_insert(title, content):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    sql = 'INSERT INTO article(title, content) VALUES("{title}", "{content}")'.format(title = title, content = content)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    #items = list(filter(lambda d: os.path.isfile('%s/%s' % (dir_path, d)) and d[0] != '.', get_items_of_dir(dir_path)))
    #for item in items[11:]:
    #    print(item)
    #    db_insert(item.split('.')[0], get_text(item))
    with open('result.txt', 'wb') as fi:
        fi.write(db_select(64, 'content'))
