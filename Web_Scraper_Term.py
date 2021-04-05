import datetime
import mysql.connector
import os
import re
import requests
import telegram
from bs4 import BeautifulSoup
from requests_html import HTMLSession

class Sites:

    def __init__(self, Sitename, Main_Address, Scrape_Address, Type, List_Query, Link_Query, Postnum_Query, Title_Query, Author_Query, js_Included = False):
        self.site_name = Sitename
        self.site_main_address = Main_Address
        self.site_scrape_address = Scrape_Address
        self.site_type = Type
        self.site_list_query = List_Query
        self.site_link_query = Link_Query
        self.site_postnum_query = Postnum_Query
        self.site_title_query = Title_Query
        self.site_author_query = Author_Query
        self.js_inlcuded = js_Included

    def create_site_table(self):

        create_table_query = (
            "CREATE TABLE {0} ".format(self.site_name) +
            "(ID int NOT NULL AUTO_INCREMENT PRIMARY KEY,"
            "sitename VARCHAR(20) DEFAULT '" + self.site_name +  "'," 
            "type VARCHAR(20) DEFAULT '" + self.site_type +  "',"
            "postdate DATETIME,"
            "postnum int,"
            "title NVARCHAR(255),"
            "author NVARCHAR(50),"
            "link VARCHAR(255))")
        return create_table_query

    def add_column_to_table(self, new_column, datatype):

        alter_table_qurey = (
            "ALTER TABLE {0} ".format(self.site_name) +
            "ADD {0} {1}".format(new_column, datatype)
        )
        return alter_table_qurey

    def delete_element_from_table(self):
       
        delete_query = ("DELETE FROM {0} ".format(self.site_name) + 
        "WHERE ID > 0"
        )
        return delete_query

    def add_feed_to_table(self, Postnum, Title, Author, Link):
        
        feed_to_table_query = (
            "INSERT INTO {0} ".format(self.site_name) +
            "(postdate, postnum, title, author, link)"
            "VALUES ('{0}', {1}, \"{2}\", \"{3}\", \"{4}\")".format(
                datetime.datetime.now(),
                Postnum,
                Title,
                Author,
                Link))

        return feed_to_table_query

# MySQL Connection Configuration
config = {
    'host' :'localhost',
    'user' : 'root',
    'password' : 'ys123372',
    'auth_plugin' : 'mysql_native_password',
    'database' : 'feeddb'
}

# Telegram Bot Configuration
bot = telegram.Bot(token = '1422791065:AAH_txqti5v5CbuRNTtgU-OEw7eTvpkmUfw')
chat_id = 1327186896

khu_general = Sites(
    Sitename='khu_general',
    Main_Address= 'http://khu.ac.kr/kor/notice/',
    Scrape_Address= 'http://khu.ac.kr/kor/notice/list.do?category=GENERAL&page=1',
    Type= 'University',
    List_Query= 'td',
    Link_Query= 'col02',
    Postnum_Query= 'seq',
    Title_Query= 'txt06',
    Author_Query= 'tit txtWriter')
khu_undergraduate = Sites(
    Sitename='khu_undergraduate',
    Main_Address= 'http://khu.ac.kr/kor/notice/',
    Scrape_Address= 'http://khu.ac.kr/kor/notice/list.do?category=UNDERGRADUATE&page=1',
    Type= 'University',
    List_Query= 'td',
    Link_Query = 'col02',
    Postnum_Query= 'seq',
    Title_Query= 'txt06',
    Author_Query= 'tit txtWriter')
khu_scholarship = Sites(
    Sitename='khu_scholarship',
    Main_Address= 'http://khu.ac.kr/kor/notice/',
    Scrape_Address= 'http://khu.ac.kr/kor/notice/list.do?category=SCHOLARSHIP&page=1',
    Type= 'Scholarship',
    List_Query= 'td',
    Link_Query = 'col02',
    Postnum_Query= 'seq',
    Title_Query= 'txt06',
    Author_Query= 'tit txtWriter')
ppomppu = Sites(
    Sitename='ppomppu',
    Main_Address= 'http://www.ppomppu.co.kr/zboard/',
    Scrape_Address= 'http://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu&search_type=sub_memo&keyword=%C7%D8%C7%C7%B8%D3%B4%CF',
    Type= 'Shopping',
    List_Query= '',
    Link_Query = ['list0', 'list1'],
    Postnum_Query= 'no',
    Title_Query= 'view_title2',
    Author_Query= 'view_cate')
saramin = Sites(
    Sitename='saramin',
    Main_Address= 'https://www.saramin.co.kr',
    Scrape_Address= 'https://www.saramin.co.kr/zf_user/jobs/list/curation?panel_type=domestic&curation_seq=634&sort=RD&is_param=0&tab_type=all&recruit_kind=recruit&quick_apply=n',
    Type= 'Job',
    List_Query= '',
    Link_Query = 'job_tit',
    Postnum_Query= 'rec_idx',
    Title_Query= 'tit_job',
    Author_Query= 'company',
    js_Included= True)

# Scholarship site
# https://www.dreamspon.com/contest/contest03.html

# Connect to MySQL DB
feeddb = mysql.connector.connect(**config)
mycursor = feeddb.cursor()

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
def update_feeds(URLs):

    # Connect to MySQL DB
    feeddb = mysql.connector.connect(**config)
    mycursor = feeddb.cursor()

    # To check hoy many new posts has been retrieved
    new_post_index = 0

    for url in URLs:

        # Latest post number from DB for comparison
        mycursor.execute("SELECT postnum FROM {0} ORDER BY postnum DESC LIMIT 1".format(url.site_name))
        current_latest_postnum = mycursor.fetchone()

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

                mycursor.execute(feed_to_table_query)
                # Apply changes to DB
                feeddb.commit()

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

                mycursor.execute(feed_to_table_query)

                # Apply changes to DB
                feeddb.commit()

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
    mycursor.close()
    feeddb.close()

    # How many new post has been retrieved
    if (new_post_index == 1):
        print(new_post_index, "new feed discovered in this iteration\n")
    elif (new_post_index > 1):
        print(new_post_index, "new feeds discovered in this iteration\n")
    else:
        print("no new feed discovered in this iteration\n")

# Scrape URL list
URLs = [khu_general, khu_scholarship, khu_undergraduate, ppomppu, saramin]
update_feeds(URLs)

'''
# Delete everything in the table for test purpose
for url in URLs:
    mycursor.execute(url.delete_element_from_table())
feeddb.commit()
'''

#mycursor.execute(saramin.create_site_table())