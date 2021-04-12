import sqlite3

site_feed_query = (
    "CREATE TABLE IF NOT EXISTS \"?\" "
    "(ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
    "sitename TEXT DEFAULT ?," 
    "type TEXT DEFAULT ?,"
    "postdate TEXT,"
    "postnum INTEGER,"
    "title TEXT,"
    "author TEXT,"
    "link TEXT)")

site_data_query = (
    "CREATE TABLE IF NOT EXISTS sitedata "
    "(sitename TEXT ," 
    "main_address TEXT ,"
    "scrape_address TEXT,"
    "sitetype TEXT,"
    "list_query TEXT,"
    "link_query TEXT,"
    "postnum_query INTEGER,"
    "title_query TEXT,"
    "author_query TEXT,"
    "js_included INTEGER)")

sitename = "khu_general"
sitetype = "University"
con = sqlite3.connect('test.db')
cur = con.cursor()


cur.execute(site_feed_query, (sitename, sitename, sitetype))
cur.execute("SELECT * FROM ?", (sitename,))
print(cur.fetchall())

con.commit()