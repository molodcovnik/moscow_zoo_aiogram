import random
import sqlite3 as sq


async def db_zoo_connect():

    global db, cur

    db = sq.connect('zoo.db')
    cur = db.cursor()

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (
                    uid INTEGER PRIMARY KEY NOT NULL,
                    user_name TEXT,
                    name TEXT,
                    last_name TEXT,
                    date_of_birth TEXT,
                    agreement TEXT,
                    result  INTEGER DEFAULT 0,
                    data_joined DATETIME NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
                    FOREIGN KEY (result)  REFERENCES animals (id) ON DELETE CASCADE );''')

    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                question TEXT);''')

    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                question_id INTEGER,
                answer TEXT,
                FOREIGN KEY (question_id)  REFERENCES questions (id) ON DELETE CASCADE ); ''')

    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT,
                a_id_1 INTEGER,
                a_id_2 INTEGER,
                a_id_3 INTEGER,
                a_id_4 INTEGER,
                a_id_5 INTEGER,
                image TEXT,
                FOREIGN KEY (a_id_1)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_2)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_3)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_4)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_5)  REFERENCES answers (id) ON DELETE CASCADE ); ''')

    cur.execute(
        ''' CREATE TABLE IF NOT EXISTS user_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                user_id INTEGER  UNIQUE,
                a_id_1 INTEGER,
                a_id_2 INTEGER,
                a_id_3 INTEGER,
                a_id_4 INTEGER,
                a_id_5 INTEGER,
                FOREIGN KEY (user_id)  REFERENCES users (uid) ON DELETE CASCADE,
                FOREIGN KEY (a_id_1)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_2)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_3)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_4)  REFERENCES answers (id) ON DELETE CASCADE,
                FOREIGN KEY (a_id_5)  REFERENCES answers (id) ON DELETE CASCADE ); ''')

    db.commit()

async def registration_user_answers(user_id, a_id_1, a_id_2, a_id_3, a_id_4, a_id_5):
    cur.execute("INSERT INTO user_answers (user_id, a_id_1, a_id_2, a_id_3, a_id_4, a_id_5) VALUES(?, ?, ?, ?, ?, ?);",
                (user_id, a_id_1, a_id_2, a_id_3, a_id_4, a_id_5))
    db.commit()


def registration_animal(name, a_id_1, a_id_2, a_id_3, a_id_4, a_id_5, image):
    cur.execute("INSERT INTO animals (name, a_id_1, a_id_2, a_id_3, a_id_4, a_id_5, image) VALUES(?, ?, ?, ?, ?, ?, ?);",
                (name, a_id_1, a_id_2, a_id_3, a_id_4, a_id_5, image))
    db.commit()


async def registration_user(uid, user_name, name, last_name, date_of_birth, agreement):
    d = date_of_birth.split('-')
    correct_date = f'{d[2]}-{d[1]}-{d[0]}'
    cur.execute("INSERT INTO users (uid, user_name, name, last_name, date_of_birth, agreement) VALUES(?, ?, ?, ?, ?, ?);", (uid, user_name, name, last_name, correct_date, agreement,))
    db.commit()


async def check_user_in_user_answers(uid):
    check = cur.execute("SELECT user_id FROM user_answers WHERE user_id = ?;", (uid,))
    db.commit()
    if check.fetchone():
        return True


def registration_question(question):
    cur.execute("INSERT INTO questions (question) VALUES(?);", (question,))
    db.commit()


def update_question(question):
    cur.execute("UPDATE answers SET answer = ? WHERE id = 14;", (question,))
    db.commit()


def registration_answer(question_id, answer):
    cur.execute("INSERT INTO answers (question_id ,answer) VALUES(?, ?);", (question_id, answer,))
    db.commit()


async def get_results(uid):

    res = cur.execute(
                     """SELECT a.name, a.image, a.id
                        from animals a JOIN user_answers u on u.a_id_1 = a.a_id_1
                        and u.a_id_2 = a.a_id_2
                        and u.a_id_3 = a.a_id_3
                        and u.a_id_4 = a.a_id_4
                        and u.a_id_5 = a.a_id_5
                        WHERE u.user_id = ?;""", (uid,)
    )

    results = res.fetchone()

    if results is not None:
        test_result = results[2]
        cur.execute('UPDATE users SET result = ? WHERE uid = ?;', (test_result, uid,))
        db.commit()
        return results
    else:
        res = cur.execute(
            """SELECT a.name, a.image, a.id
               from animals a JOIN user_answers u on u.a_id_1 = a.a_id_1
               and u.a_id_2 = a.a_id_2
               and u.a_id_5 = a.a_id_5
               WHERE u.user_id = ?;""", (uid,)
        )

        short_results = res.fetchall()
        result = random.choice(short_results)
        test_result = result[2]
        cur.execute('UPDATE users SET result = ? WHERE uid = ?;', (test_result, uid,))
        db.commit()
        return result


async def get_questions(i):
    cur.execute('SELECT question FROM questions WHERE id = ?;', (i,))
    db.commit()
    return cur.fetchone()[0]


async def get_ikb_for_answer(i):
    cur.execute('SELECT id, answer FROM answers WHERE question_id = ?;', (i,))
    db.commit()
    return cur.fetchall()


async def get_animal(uid):
    cur.execute("""SELECT a.name
                    FROM animals a
                    JOIN users u ON a.id = u.result
                    WHERE uid = ?;""", (uid, ))
    db.commit()
    return cur.fetchone()

async def check_result_test(uid):
    cur.execute('SELECT result FROM users WHERE uid = ?;', (uid,))
    db.commit()
    return cur.fetchone()


async def get_user_data(uid):
    cur.execute('SELECT name, last_name, date_of_birth, result FROM users WHERE uid = ?;', (uid,))
    db.commit()
    return cur.fetchone()


async def check_user_on_reg(uid):
    check = cur.execute("SELECT uid, agreement FROM users WHERE uid = ?;", (uid,))
    db.commit()
    if check.fetchone():
        return True


async def reset_result(uid):
    cur.execute('DELETE from user_answers WHERE user_id = ?;', (uid,))
    cur.execute('UPDATE users set result = 0 where uid = ?;', (uid,))
    db.commit()


async def reset_result_for_nonauth(uid):
    cur.execute('DELETE from user_answers WHERE user_id = ?;', (uid,))
    db.commit()
