"""Здась находятся модели базы данных, а также запросы"""


def create_table_users(cursor, connect):
    """Создается таблица пользователей (users), если
    ее не существует в БД.
    user_id - первичный ключ,
    username - имя пользователя.
    """

    cursor.execute("""CREATE TABLE IF NOT EXISTS users
                    (user_id INTEGER PRIMARY KEY,                      
                    username VARCHAR)""")
    connect.commit()


def create_table_tasks(cursor, connect):
    """Создается таблица задач (tasks), если
        ее не существует в БД.
        id - первичный ключ,
        user_id - имя пользователя, внешний ключ
        text - текст задачи,
        time - время исполнения задачи,
        is_checked - состояние выделенной задачи, в sqlite3 нет bool, поэтому пришлось использовать 1/0 :(
        Также реализовано каскадное удаление всех задач пользователя
        при удалении записи пользоватея в таблице users.
        """

    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks 
                    (id INTEGER PRIMARY KEY, 
                    user_id INTEGER NOT NULL, 
                    text VARCHAR NOT NULL, 
                    time DATETIME ,
                    is_checked INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) 
                    REFERENCES users(user_id) ON DELETE CASCADE)""")

    connect.commit()


def set_user(cursor, connect, id, username=''):
    """Вставляем запись пользователя в БД"""

    query = """INSERT OR IGNORE INTO users(user_id, username)
                    VALUES (?, ?)"""
    data_tuple = (id, username)
    cursor.execute(query, data_tuple)
    connect.commit()


def get_user(cursor, user_id):
    """Получаем запись пользователя по user_id в БД"""

    query = """SELECT * FROM users
                    WHERE user_id = ?"""
    data_tuple = (user_id,)
    cursor.execute(query, data_tuple)
    res = cursor.fetchall()
    return res


def del_user(cursor, connect, user_id):
    """Удаляем запись пользователя по user_id в БД"""

    query = """DELETE from users
                        WHERE user_id = ? """
    data_tuple = (user_id,)
    cursor.execute(query, data_tuple)
    connect.commit()


def set_task(cursor, connect, user_id, text, time):
    """Вставляем запись задачи в БД"""

    query = """INSERT OR IGNORE INTO tasks( user_id, text, time)
                    VALUES (?, ?, ?)"""
    data_tuple = (user_id, text, time)
    cursor.execute(query, data_tuple)
    connect.commit()


def get_tasks(cursor, user_id):
    """Получаем все задачи пользователя по user_id в БД"""

    query = """SELECT * FROM tasks
                WHERE user_id = ?"""
    data_tuple = (user_id, )
    cursor.execute(query, data_tuple)
    res = cursor.fetchall()
    return res


def get_tasks_time_not_null(cursor):
    """Получаем все задачи, в которых определено время исполнения"""

    query = """SELECT * FROM tasks
                WHERE time IS NOT NULL"""

    cursor.execute(query)
    res = cursor.fetchall()
    return res


def del_task(cursor, connect, id, user_id):
    """Удаляем задачу по id задачи и user_id в БД"""

    query = """DELETE from tasks
                    WHERE id = ? and user_id = ?"""
    data_tuple = (id,user_id)
    cursor.execute(query, data_tuple)
    connect.commit()


def del_checked_tasks(cursor, connect, user_id):
    """Удаляем выделенные задачи пользователя по user_id в БД"""

    query = """DELETE from tasks
                        WHERE user_id = ? AND is_checked = 1"""
    data_tuple = (user_id, )
    cursor.execute(query, data_tuple)
    connect.commit()


def change_check_task(cursor, connect,id, user_id):
    """Меняем состояние выделенности задачи пользователя на противоположное"""

    query_get_state_task = """SELECT is_checked FROM tasks
                    WHERE id = ? AND user_id = ?"""


    data_tuple = (id, user_id)
    cursor.execute(query_get_state_task, data_tuple)
    list_state = cursor.fetchall()
    if len(list_state)==1:
        query_update = """UPDATE tasks
                               SET is_checked = ? 
                               WHERE id = ? AND user_id = ?"""
        update_data_tuple = (0 if list_state[0][0] else 1, id, user_id)

        cursor.execute(query_update, update_data_tuple)
        connect.commit()

