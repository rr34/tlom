import sys
import mariadb

# takes mysql text and a tuple of the user input values and returns the results in cursor format. 
def sql_execute(text, user_input):
    try:
        conn = mariadb.connect(
            user="carruffsite",
            host="127.0.0.1",
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

    conn.close()

    return cur