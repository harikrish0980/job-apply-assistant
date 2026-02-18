import sqlite3

conn = sqlite3.connect("data/db.sqlite3")
cur = conn.cursor()

cur.execute("DELETE FROM targets WHERE company_token='careers'")
conn.commit()

print("Deleted rows:", cur.rowcount)

conn.close()
