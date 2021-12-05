import os
import requests
import sqlite3
import telegram
import time
from bs4 import BeautifulSoup
from datetime import datetime
from re import compile
from selenium import webdriver
from .db import _instance_path
from flask import flash

def tuple_to_sitedata_dict(**kwargs):
    """ (**kwargs) -> dictionary

    Receive value from sitedata table, with a corresponding key.

    if there are multiple values in a single sitedata column, split them with a "," and make it a single list.

    >>> tuple_to_sitedata_dict(a = "1", b = "2, 3", c = "asd")
    {"a" : 1, "b" : ["2", "3"], "c" : "asd"}
    """
    for key, value in kwargs.items():
        if type(value) is str and "," in value:
            kwargs[key] = value.split(sep="," )
    return kwargs
def extract_post_number(href, query):
    if query == "/":
        postnum = [int(s) for s in href.split("/") if s.isdigit()][0]
        return postnum
    else:
        postnum = [s for s in href.split("?")[1].split("&") if query in s][0]
        return int(postnum[len(query) + 1:])

# Obslete extract number function 
    '''
def extract_post_number(href, query):
    """ (str, str) -> int

    Extract post number from site link, with a predetermined query to specify location of post number.

    >>> extract_post_number("https://www.aaaaa.com/?no=123456", "no")
    123456
    """
    href_postnum_list = []
    href_postnum = 0

    # index of query inside of link string
    query_index = href.find(query)
    # if query is "no" and link includes no=123...
    # search_start_index points to 1
    search_start_index = query_index + len(query) + 1

    for i in range(int(search_start_index), len(href)):
        if href[i].isdigit():
            # Temporary reversed list of post number
            href_postnum_list.insert(0, int(href[i]))
        else:
            # Finish searching upon reaching nondigit
            break

    # Return ordered int from reversed list
    for i in range(len(href_postnum_list)):
        href_postnum += (href_postnum_list[i] * 10**i)

    return href_postnum
    '''

def update_feed():
    try:
        # Telegram Bot Configuration
        bot = telegram.Bot(token = '1822963809:AAEKMWyn9uBHXQ_m6D4yctWLcmC9bpsU8us')
        chat_id = 1327186896

        # Connect to sqlite3 DB
        con = sqlite3.connect(os.path.join(_instance_path, 'data.db'))
        cur = con.cursor()
        URLs = cur.execute("SELECT * FROM sitedata").fetchall()  

        # For debugging purpose
        print("running scraper at {}...".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S")))  

        # To check hoy many new posts has been retrieved
        new_post_index = 0

        # Convert sitadata tuple to dictionary with keys
        for url_tuple in URLs:
            # Reset page count
            page_count = 0

            url = tuple_to_sitedata_dict(
                sitename = url_tuple[0],
                main_address = url_tuple[1],
                scrape_address = url_tuple[2],
                sitetype = url_tuple[3],
                link_query = url_tuple[4],
                postnum_query = url_tuple[5],
                title_query = url_tuple[6],
                author_query = url_tuple[7],
                sitecolor = url_tuple[8])

            # Latest post number from DB for comparison
            current_latest_postnum = cur.execute(
                "SELECT postnum FROM sitefeed WHERE sitename = ? ORDER BY postnum DESC LIMIT 1", (url["sitename"],)).fetchone()

            # Using selenium
            options = webdriver.FirefoxOptions()
            options.binary = "/usr/lib/firefox/firefox"
            options.headless = True
            browser = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", firefox_options=options)

            # Open browser
            browser.get(url["scrape_address"])
            time.sleep(5)
            bs = BeautifulSoup(browser.page_source, 'html.parser')
            
            # After getting page source, close browser
            browser.close()

            #To identify feed link
            bs_results = bs.find_all(class_ = url["link_query"])

            # Link query None-check procedure
            if bs_results == []:
                raise Exception("Link query")

            # Dive into each page element
            for page in bs_results:
                temp_link = page.find('a', href = compile(url["postnum_query"]))

                # Filter garbage value for khu sites
                if temp_link is None:
                    continue
                
                if url["scrape_address"] == url["main_address"]:
                    page_link = temp_link['href'].strip()
                else:
                    page_link = url["main_address"] + temp_link['href'].strip()

                page_postnum = extract_post_number(page_link, url["postnum_query"])

                # Control flow before going deep into the link to save time
                if (current_latest_postnum is not None and page_postnum <= current_latest_postnum[0]):
                    print('No more new feeds for {0}\n'.format(url["sitename"]))
                    break

                # Using selenium
                options = webdriver.FirefoxOptions()
                options.binary = "/usr/lib/firefox/firefox"
                options.headless = True
                browser = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", firefox_options=options)

                # Open browser
                browser.get(page_link)
                bs2 = BeautifulSoup(browser.page_source, 'html.parser')

                # After getting page source, close browser
                browser.close()

                # Find postdate, title, author in the link
                page_postdate = datetime.now().strftime("%Y/%m/%d %H:%M")
                page_title = bs2.find(class_ = url["title_query"]).text.strip()
                # Title None-check procedure
                if page_title is None:
                    raise Exception("Title")

                page_author = bs2.find(class_ = url["author_query"]).text.strip()
                page_author = page_author.split()[0]

                # Author None-check procedure
                if page_title is None:
                    raise Exception("Author")
                        
                insert_feed_query = (
                    "INSERT INTO sitefeed "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                )

                insert_tuple = (
                url["sitename"], url["sitetype"], page_postdate, page_postnum, page_title, page_author, page_link, url["sitecolor"])

                # Add new feed to the Table
                cur.execute(insert_feed_query, insert_tuple)
                # Apply changes to DB
                con.commit()

                # replace < or > so that HTML parser understands as text
                page_sitename = url['sitename'].upper()

                temp_text = [page_sitename, page_author, page_title]
                for i in range(len(temp_text)):
                    if "<" in temp_text[i] or ">" in temp_text[i]:
                        temp_text[i] = temp_text[i].replace("<", "&lt;")
                        temp_text[i] = temp_text[i].replace(">", "&gt;")

                bot_text = '<b>{0}</b>\n  {1}\n\n<b>{2}</b>\n\n <a href = "{3}">Link</a>'.format(
                    temp_text[0], temp_text[1], temp_text[2], page_link)

                # Send real-time notification
                bot.send_message(
                    chat_id = chat_id, 
                    text= bot_text,
                    parse_mode = 'HTML')

                new_post_index += 1
                page_count += 1
                if (page_count) >= 5:
                    break
                
        # Close session
        cur.close()
        con.close()

        # How many new post has been retrieved
        prepending_text = "Manual update procedure finished.\n\n"
        if (new_post_index == 1):
            return prepending_text + str(new_post_index) + " new feed discovered in this iteration"
        elif (new_post_index > 1):
            return prepending_text + str(new_post_index) + " new feeds discovered in this iteration"
        else:
            return prepending_text + "No new feed discovered in this iteration"
        
    except Exception as e:
        prepending_text = "Manual update procedure failed while scraping {0}.\n".format(url["sitename"])
        if str(e) in ["Link query", "Title", "Post number", "Author"]:
            return prepending_text + "None returned while scraping {0}.".format(str(e))
        else:
            return prepending_text + str(e)
def test_feed(url):
    try:
        # Using selenium
        options = webdriver.FirefoxOptions()
        options.binary = "/usr/lib/firefox/firefox"
        options.headless = True
        browser = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", firefox_options=options)

        # Open browser
        browser.get(url["scrape_address"])
        time.sleep(2)
        bs = BeautifulSoup(browser.page_source, 'html.parser')

        # After getting page source, close browser
        browser.close()

        # Page address None-check procedure
        if bs is None:
            return "No result returned using current page address."

        # To identify feed link
        bs_results = bs.find_all(class_ = url["link_query"])
        # Link query None-check procedure
        if bs_results is None:
            return "No result returned using current query for link."

        for page in bs_results:            
            temp_link = page.find('a', href = compile(url["postnum_query"]))
            
            # Filter garbage value for khu sites
            if temp_link is None:
                continue

            if url["scrape_address"] == url["main_address"]:
                page_link = temp_link['href'].strip()
            else:
                page_link = url["main_address"] + temp_link['href'].strip()

            options = webdriver.FirefoxOptions()
            options.binary = "/usr/lib/firefox/firefox"
            options.headless = True
            browser = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", firefox_options=options)

            # Open browser
            browser.get(page_link)
            bs2 = BeautifulSoup(browser.page_source, 'html.parser')

            # After getting page source, close browser
            browser.close()

            # Find title, author in the link
            page_title = bs2.find(class_ = url["title_query"]).text.strip()
            # Title None-check procedure
            if page_title is None:
                return "No result returned using current query for title."

            page_author = bs2.find(class_ = url["author_query"]).text.strip()
            page_author = page_author.split()[0]

            # Author None-check procedure
            if page_title is None:
                return "No result returned using current query for author."

            return "success"
    except Exception as e:
        return(str(e))
