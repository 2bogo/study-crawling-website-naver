from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
import time
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm

def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [(start + timedelta(days=i)).strftime("%Y.%m.%d") for i in range((end-start).days+1)]
    return dates

def searchTotalLink(date):
    lastLink = ""
    totalLink = []
    page = 1
    joinedDate = ''.join(date.split('.'))
    while True:
        addr = f"https://search.daum.net/search?w=news&DA=STC&enc=utf8&cluster=y&cluster_page=1&q=%EA%B2%BD%EB%82%A8&period=u&sd={date}000000&ed={date}235959&p={page}"
        driver.get(addr)
        time.sleep(1)
        html = driver.page_source
        dom = BeautifulSoup(html, "lxml")
        select_raw = dom.find_all("a", {"class" : "f_nb"})
        links = [selected.attrs['href'] for selected in select_raw]

        if lastLink == links[-1]:
            break
        else:
            lastLink = links[-1]
            totalLink += links
            page += 1
    return totalLink

def crawlingComments(addr):
    driver.get(addr)
    time.sleep(1)
    pages = 0
    
    try:
        while True:
            driver.find_element_by_css_selector(".link_fold").click()
            time.sleep(1.5)
            pages+=1
            
    except exceptions.ElementNotVisibleException as e: # 페이지 끝
        pass
    
    except Exception as e:
        pass
        
    html = driver.page_source
    dom = BeautifulSoup(html, "lxml")
    
    title_raw = dom.find_all("h3", {"class" : "tit_view"})
    
    try:
        title = [x.text for x in title_raw][0]
    except:
        title = title_raw
    
    
    comments_raw = dom.find_all("p", {"class" : "desc_txt"})
    if comments_raw == []:
        pass
    else:
        comments = [[title, comment.text, addr] for comment in comments_raw]
        return comments
    
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome('/home/ezy/Downloads/chromedriver', options=options)

dates = date_range("2021-7-21", "2021-07-21")

totalLinks = [searchTotalLink(x) for x in tqdm(dates)]

totalLinks = sum(totalLinks, [])

import pickle

with open('totalLinks.pkl', 'wb') as f:
    pickle.dump(totalLinks, f)
    
    
data = [crawlingComments(addr) for addr in tqdm(totalLinks)]

data = list(filter(None, data))

data = sum(data, [])

data = np.stack(data)
df = pd.DataFrame(data, columns=['title', 'comment', 'link'])

df.to_pickle('daumComment.pk')

driver.close()