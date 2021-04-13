import mysql.connector
import os
import re
import requests
import sqlite3
import telegram
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from . import Instance_Path

# Telegram Bot Configuration
bot = telegram.Bot(token = '1422791065:AAH_txqti5v5CbuRNTtgU-OEw7eTvpkmUfw')
chat_id = 1327186896

# Connect to sqlite3 DB
con = sqlite3.connect(os.path.join(Instance_Path, 'data.db'))
cur = con.cursor()

def extract_post_number(href, query):

    href_postnum_list = []
    href_postnum = 0
    query_index = href.find(query)
    search_start_index = query_index + len(query) + 1

    for i in range(int(search_start_index), len(href)):
        if href[i].isdigit():
            # Temporary reversed list of post number
            href_postnum_list.insert(0, int(href[i]))
        else:
            break

    # Return ordered int from reversed list
    for i in range(len(href_postnum_list)):
        href_postnum += (href_postnum_list[i] * 10**i)

    return href_postnum
def update_feed():

    # Connect to sqlite3 DB
    con = sqlite3.connect(os.path.join(Instance_Path, 'data.db'), detect_types= )
    cur = con.cursor()
    URLs_list = cur.execute("SELECT * FROM sitedata").fetchall()
    for element in URLs_list:
        

    # To check hoy many new posts has been retrieved
    new_post_index = 0

    for url in URLs:

        # Latest post number from DB for comparison
        cur.execute("SELECT postnum FROM sitefeed WHERE sitename = ? ORDER BY postnum DESC LIMIT 1", (url[0],))
        current_latest_postnum = cur.fetchone()

        # Send HTTP request to the given URL
        # Retrieves the HTML data that server sends
        page = requests.get(url.site_scrape_address)

        # Construct BeautifulSoup
        bs = BeautifulSoup(page.content, 'html.parser')

        #To identify feed link
        bs_results = bs.find_all(url.site_list_query, class_ = url.site_link_query)

        # Extract information from feed
        for page in bs_results:
            
            temp_link = page.find('a', href = re.compile(url.site_postnum_query))
            page_link = url.site_main_address + temp_link['href']

            if(url.js_inlcuded): # If a site uses Javascript
                # Create an HTML Session object
                session = HTMLSession()

                # Use the object above to connect to needed webpage
                js_resp = session.get(page_link)

                # Run JavaScript code on webpage
                js_resp.html.render()

                # Construct BeautifulSoup
                bs2 = BeautifulSoup(js_resp.html.html, 'html.parser')
            else: # No Javascript
                # Send HTTP request to the given URL
                # Retrieves the HTML data that server sends
                link_resp = requests.get(page_link)

                # Construct BeautifulSoup
                bs2 = BeautifulSoup(link_resp.content, 'html.parser')

            # Find title, author in the link
            page_postnum = extract_post_number(page_link, url.site_postnum_query)
            page_title = bs2.find(class_ = url.site_title_query).text.strip()
            page_author = bs2.find(class_ = url.site_author_query).text.strip()

            print(page_postnum)
            print(page_title)
            print(page_author)
            print(page_link)

            if None in (page_title, temp_link):
                print('None detected among title, and link')
                continue
            
            # initial Data
            if (current_latest_postnum is None):
                # Add new feed to the Table
                feed_to_table_query = url.add_feed_to_table(page_postnum, page_title, page_author, page_link)

                cur.execute(feed_to_table_query)
                # Apply changes to DB
                con.commit()

                # Send real-time notification
                bot_text = '<b> {0}</b>\n {1}\n\n<b>{2}</b>\n\n <a href = "{3}">Link</a>'.format(url.site_name.upper(), page_author, page_title, page_link)

                bot.send_message(
                    chat_id = chat_id, 
                    text= bot_text,
                    parse_mode = 'HTML')
                new_post_index += 1
                break
            # New feed discovered
            elif (page_postnum > current_latest_postnum[0]): 
                # Add new feed to the Table
                feed_to_table_query = url.add_feed_to_table(page_postnum, page_title, page_author, page_link)

                cur.execute(feed_to_table_query)

                # Apply changes to DB
                con.commit()

                # Send real-time notification
                bot_text = '  <b>{0}</b>\n  {1}\n\n<b>{2}</b>\n\n <a href = "{3}">Link</a>'.format(url.site_name.upper(), page_author, page_title, page_link)

                bot.send_message(
                    chat_id = chat_id, 
                    text= bot_text,
                    parse_mode = 'HTML')

                new_post_index += 1
            # No new feeds
            else:
                print('No more new feeds for {0}\n'.format(url.site_name))
                break

    # Close the session
    cur.close()
    con.close()

    # How many new post has been retrieved
    if (new_post_index == 1):
        print(new_post_index, "new feed discovered in this iteration\n")
    elif (new_post_index > 1):
        print(new_post_index, "new feeds discovered in this iteration\n")
    else:
        print("no new feed discovered in this iteration\n")

# Scrape URL list
update_feed()