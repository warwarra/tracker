"""sql-database and console interface"""
from sqlite3 import connect
from os.path import isfile
from re import match, sub, split, search
from datetime import datetime

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
    inner_cursor.execute("""CREATE TABLE references
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
    #вывод
    print('Done!')

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
    #вывод
    print('Done!')

if __name__ == '__main__':
    #подключение к бд (и её создание)
    if not isfile("database.db"):
        CONN, CURSOR = db_connect()
        create_db(CONN, CURSOR)
    else:
        CONN, CURSOR = db_connect()

    while True:
        INPUT_STRING = input("Command: ")
        INPUT_STRING = sub(" ", "", INPUT_STRING)
        RESULT = match(r"input_tags:", INPUT_STRING)
        if RESULT:
            INPUT_STRING = INPUT_STRING[RESULT.end():]
            INPUT_TAGS = split(r',', INPUT_STRING)
            input_tags(CONN, CURSOR, INPUT_TAGS)
        else:
            RESULT = match(r"input_resources:", INPUT_STRING)
            if RESULT:
                INPUT_STRING = INPUT_STRING[RESULT.end():]
                INPUT_LINKS = split(r',', INPUT_STRING)
                input_resources(CONN, CURSOR, INPUT_LINKS)
            else:
                print('This command is not supported.')
