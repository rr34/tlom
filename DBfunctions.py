import sys
import mariadb
import mysql.connector
from flask import jsonify

# takes mysql text and a tuple of the user input values and returns the results in cursor format. 
def sql_execute(text, user_input, result_type):
    try:
        # conn = mariadb.connect(
        #     user="carruffsite",
        #     host="127.0.0.1",
        #     port=3306,
        #     database="carruffdb"
        # )
        conn = mariadb.connect(
            user="nate",
            host="108.174.197.50",
            port=3306,
            database="carruffdb"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB platform: {e}")
        sys.exit(1)

    # Get cursor
    cur = conn.cursor()

    if user_input:
        cur.execute(text, user_input)
    else:
        cur.execute(text)

    # description = cur.description

    result_fetched = cur.fetchall()
    if result_type == 'table':
        columns = [c[0] for c in cur.description]
        return result_fetched, columns, result_json
    elif result_type == 'json':
        result_json = jsonify(result_fetched)
        return result_json
    cur.close()
    conn.close()



def sql_execute_pd(text, user_input):
    try:
        conn = mysql.connector.connect(
            user="nate",
            host="108.174.197.50",
            port=3306,
            database="carruffdb"
        )
    except mysql.connector.Error as e:
        print(f"Error connecting to MariaDB platform: {e}")
        sys.exit(1)

    # Get cursor
    cur = conn.cursor()

    if user_input:
        cur.execute(text, user_input)
    else:
        cur.execute(text)

    conn.close()

    return cur