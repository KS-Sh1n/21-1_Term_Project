import sqlite3

sitename = "khu_general"
sitetype = "University"
con = sqlite3.connect('data.db')
cur = con.cursor()

cur.execute("SELECT * FROM sitedata")
print(cur.fetchall())

con.commit()