import psycopg2
from config import db_name, hostname, username, password
import json
def get_connection():
    try:
        conn = psycopg2.connect(
        database=db_name, 
        user=username,
        password=password, 
        host=hostname,
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"[EXCEPTION] - ", e)


def user_exists(table_name, user_tg_id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""select count(*) from {table_name} where user_tg_id = {user_tg_id};
                """
            )
            res = cursor.fetchone()
            if res[0]:
                so_conn.close()
                return True
            else:
                so_conn.close()
                return False


def set_new_user(table_name, user_tg_id, get_args=None):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""select count(*) from {table_name} where user_tg_id = {user_tg_id};
                """
            )
            res = cursor.fetchone()
            #если 0, то запись, если 1, то уже есть. Запись реферала.
            if not res[0]:
                cursor.execute(
                    f"""INSERT INTO {table_name} (user_tg_id) VALUES (%s);
                    """,
                    (user_tg_id,)
                )
                if get_args:
                    cursor.execute(
                        f"""update {table_name} set total_coins = %s, referred_by = %s where user_tg_id = %s;
                        """,
                        (100, get_args, user_tg_id,)
                    )
                else:
                    cursor.execute(
                        f"""update {table_name} set total_coins = %s where user_tg_id = %s;
                        """,
                        (50, user_tg_id,)
                    )
    so_conn.close()    


def give_coins(table_name, user_tg_id, coins):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""update {table_name} set total_coins = total_coins + %s where user_tg_id = %s;
                """,
                (coins, user_tg_id,)
            )
    so_conn.close()

def get_balance(table_name, user_tg_id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT total_coins FROM {table_name} where user_tg_id = {user_tg_id};
                """
                )
            amount = cursor.fetchone()
            so_conn.close()
            return amount[0]

def get_referral_count(table_name, user_tg_id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT count(*) FROM {table_name} where referred_by = {user_tg_id};
                """
                )
            amount = cursor.fetchone()
            so_conn.close()
            return amount[0]

def get_all_select(table_name):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT * FROM {table_name};
                """
                )
            rows = cursor.fetchall()
            for row in rows:
                print(f"id:{row[0]} - telegram_id:{row[1]} - coins:{row[2]} - referred_by:{row[3]}")
            print("\n")
    so_conn.close()

#admin

def set_new_task(table_name, channel_name, channel_link, description, reward):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO {table_name} (channel_name, channel_link, description, reward) 
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """,
                (channel_name, channel_link, description, reward)
            )

    so_conn.close()



#вывести как json
def get_tasks_for_admin(table_name):

    so_conn = get_connection()
    
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT * FROM {table_name};
                """
                )
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                task = {
                    "id": row[0],
                    "channel_name": row[1],
                    "channel_link": row[2],
                    "description": row[3],
                    "is_active": row[4],
                    "reward": row[5]
                }
                tasks.append(task)
            so_conn.close()
            return json.dumps(tasks, indent=4)

def delete_row(table_name, id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""DELETE FROM {table_name} WHERE id = {id};
                """
                )
    so_conn.close()

def check_active_task(table_name, id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT is_active FROM {table_name} WHERE id = {id};
                """
                )
            res = cursor.fetchone()
            so_conn.close()
            if res:
                return res[0]
            


def set_active_task(table_name, id, condition):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""UPDATE {table_name} SET is_active = {condition} WHERE id = {id};
                """
                )
    so_conn.close()

def count_of_active_task(table_name):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT count(*) FROM {table_name} WHERE is_active = true;
                """
                )
            res = cursor.fetchone()
            so_conn.close()
            return res[0]
    return 
def get_parsed_link(tab_tasks, id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT channel_link FROM {tab_tasks} WHERE id = {id};
                """
                )
            res = cursor.fetchone()
            so_conn.close()
            return "@" + res[0].split("/")[-1]

def get_user_completed_info(table_name, user_tg_id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT COUNT(*) FROM {table_name} WHERE user_id = {user_tg_id};
                """
                )
            status_complete = cursor.fetchone()
            so_conn.close()
            if status_complete:
                return status_complete[0]

def get_user_all_tasks_from_complete(table_name, user_tg_id):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT * FROM {table_name} WHERE user_id = {user_tg_id};
                """
                )
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                task = {
                    "id": row[0],
                    "user_id": row[1],
                    "task_id": row[2],
                    "completed": row[3],
                }
                tasks.append(task)
            so_conn.close()
            return json.dumps(tasks, indent=4)

def set_user_completed_info(table_name, user_tg_id, task_id, status_complete):
    so_conn = get_connection()
    if so_conn:
        with so_conn.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO {table_name} (user_id, task_id, completed) 
                    VALUES (%s, %s, %s);
                """,
                (user_tg_id, task_id, status_complete)
                )
            so_conn.close()



def count_of_completed():
    pass

if __name__ == "__main__":
    # print(get_user_completed_info("task_completion", 478102754))
    pass
    # print(get_parsed_link("tasks", 1))
    # print(type(count_of_active_task("tasks")))
    # check_active_task("tasks", 3)
    # set_active_task("tasks", 3, True)
    # print(type(check_active_task("tasks", 2)))
    # delete_row("tasks", 5)
    # set_new_task("tasks", "test", "terssss", "test", 100)
    # print(get_tasks_for_admin("tasks"))
    # get_all_select("users_test")