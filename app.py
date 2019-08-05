"""sql-database and console interface"""
from sqlite3 import connect
from os.path import isfile
from re import sub, split, search
from datetime import datetime
from vk_module import vk_search
ACCESS_TOKEN = "/your_token/"

def db_connect():
    """making db var and cursor"""
    inner_conn = connect("database.db")
    inner_cursor = inner_conn.cursor()
    return inner_conn, inner_cursor

def create_db(inner_conn, inner_cursor):
    """db layout"""
    inner_cursor.execute("""CREATE TABLE tags
                    (__id_request integer, __date_time text, __name_tag text)
                    """)
    inner_cursor.execute("""CREATE TABLE resources
                    (__id_request integer, __date_time text, __platform text, __link text)
                    """)
    inner_cursor.execute("""CREATE TABLE reference
                    (__date_time text, __platform text, __name_tag text, __content_message text)
                    """)
    inner_conn.commit()

def platform_identification(link):
    """platform identification and link cutting"""
    #проверка для вк
    inner_result = search(r'vk\.com/', link)
    if inner_result:
        response = ('VK', link[inner_result.start():])
    #проверка для инст
    inner_result = search(r'instagram\.com/', link)
    if inner_result:
        response = ('INST', link[inner_result.start():])
    return response

def input_tags(inner_conn, inner_cursor, tags):
    """entering tags into db"""
    #объявление переменных
    data = []
    saved_tags = []
    now = datetime.today().strftime("%H:%M %d.%m.%Y")
    #проверка таблицы на пустоту
    inner_cursor.execute("""SELECT __id_request FROM tags""")
    if inner_cursor.fetchall() == []:
        for tag in tags:
            data.append((0, now, tag))
        inner_cursor.executemany("""INSERT INTO tags VALUES (?, ?, ?)""", data)
    #если не пустая
    else:
        #чтение всех тегов
        inner_cursor.execute("""SELECT __name_tag FROM tags""")
        rows = inner_cursor.fetchall()
        for tag in rows:
            saved_tags.append(tag[0])
        #поиск последнего id
        inner_cursor.execute("""SELECT __id_request FROM tags""")
        __id = inner_cursor.fetchall()[-1][0]+1
        for tag in tags:
            #проверка на повторения
            if not tag in saved_tags:
                data.append((__id, now, tag))
        inner_cursor.executemany("""INSERT INTO tags VALUES (?, ?, ?)""", data)
    inner_conn.commit()

def input_resources(inner_conn, inner_cursor, links):
    """entering resources into db"""
    #объявление переменных
    data = []
    saved_links = []
    now = datetime.today().strftime("%H:%M %d.%m.%Y")
    #проверка таблицы на пустоту
    inner_cursor.execute("""SELECT __id_request FROM resources""")
    if inner_cursor.fetchall() == []:
        for link in links:
            platform, link = platform_identification(link)
            data.append((0, now, platform, link))
        inner_cursor.executemany("""INSERT INTO resources VALUES (?, ?, ?, ?)""", data)
    #если не пустая
    else:
        #чтение всех ссылок
        inner_cursor.execute("""SELECT __link FROM resources""")
        rows = inner_cursor.fetchall()
        for link in rows:
            saved_links.append(link[0])
        #поиск последнего id
        inner_cursor.execute("""SELECT __id_request FROM resources""")
        __id = inner_cursor.fetchall()[-1][0]+1
        for link in links:
            #проверка на повторения
            platform, link = platform_identification(link)
            if not link in saved_links:
                data.append((__id, now, platform, link))
        inner_cursor.executemany("""INSERT INTO resources VALUES (?, ?, ?, ?)""", data)
    inner_conn.commit()

def from_vk(inner_conn, inner_cursor, token):
    """search tags in vk"""
    #объявление переменных
    saved_links = []
    saved_tags = []
    #чтение всех ссылок vk
    inner_cursor.execute("""SELECT * FROM resources""")
    rows = inner_cursor.fetchall()
    for row in rows:
        if row[2] == 'VK':
            saved_links.append(row[3])
    #чтение всех тегов
    inner_cursor.execute("""SELECT __name_tag FROM tags""")
    rows = inner_cursor.fetchall()
    for tag in rows:
        saved_tags.append(tag[0])
    #поиск на странице и запись в бд
    for tag in saved_tags:
        for link in saved_links:
            data = vk_search(tag, link, token)
            inner_cursor.executemany("""INSERT INTO reference VALUES (?, ?, ?, ?)""", data)
    inner_conn.commit()

if __name__ == '__main__':
    #подключение к бд (и её создание)
    if not isfile("database.db"):
        CONN, CURSOR = db_connect()
        create_db(CONN, CURSOR)
    else:
        CONN, CURSOR = db_connect()

    INPUT_STRING = input("input_all_tags: ")
    INPUT_STRING = sub(" ", "", INPUT_STRING)
    INPUT_TAGS = split(r',', INPUT_STRING)
    input_tags(CONN, CURSOR, INPUT_TAGS)
    INPUT_STRING = input("input_all_resources: ")
    INPUT_STRING = sub(" ", "", INPUT_STRING)
    INPUT_LINKS = split(r',', INPUT_STRING)
    input_resources(CONN, CURSOR, INPUT_LINKS)

    from_vk(CONN, CURSOR, ACCESS_TOKEN)
    print('Done!')
