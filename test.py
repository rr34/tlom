import mariadb
import sys

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

cur.execute(
    """
SELECT Organization, Name, Notes
from people2_people;
"""
)
for (Organization, Name, Notes) in cur:
    print(f"Organization: {Organization}, Name: {Name}, Notes: {Notes}")