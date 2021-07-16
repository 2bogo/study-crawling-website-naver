from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
import time
import pickle
import pandas as pd
import numpy as np

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome('/home/ezy/Downloads/chromedriver', options=options)

data = []
lastLink = ""
totalLinks = []
page = 1

while True:
    addr = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EA%B2%BD%EB%82%A8&sort=0&photo=0&field=0&pd=5&ds=2020.07.17&de=2021.07.17&cluster_rank=32&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:1y,a:all&start={page}"
    driver.get(addr)
    time.sleep(1)
    html = driver.page_source
    dom = BeautifulSoup(html, "lxml")
    try:
        if "검색결과가 없습니다." in [x.text for x in dom.find_all("div", {"class" : "not_found02"})][0]:
            break
    except:
        select_raw = dom.find_all("a", {"class" : "info"})
        links = [selected.attrs['href'] for selected in select_raw]
        
        if lastLink == links[-1]:
            break
        else:
            lastLink = links[-1]
                
        naver_links = [x.split('mode=LSD')[0] + "m_view=1&includeAllCount=true&mode=LSD" + x.split('mode=LSD')[1] for x in links if 'naver' in x and 'mode=LSD' in x]
        totalLinks += naver_links
        page += 10

def crawlingComments(addr):
    driver.get(addr)
    time.sleep(1)
    pages = 0
    
    try:
        while True:
            driver.find_element_by_css_selector(".u_cbox_btn_more").click()
            time.sleep(1.5)
            pages+=1
            
    except exceptions.ElementNotVisibleException as e: # 페이지 끝
        pass
    
    except Exception as e:
        pass
        
    html = driver.page_source
    dom = BeautifulSoup(html, "lxml")
    
    title_raw = dom.find_all("h3", {"id" : "articleTitle"})
    
    title = [x.text for x in title_raw][0]
    
    
    comments_raw = dom.find_all("span", {"class" : "u_cbox_contents"})
    if comments_raw == []:
        pass
    else:
        comments = [[title, comment.text, addr] for comment in comments_raw]
        return comments

data = [crawlingComments(addr) for addr in totalLinks]

data = list(filter(None, data))

data = sum(data, [])

data = np.stack(data)
df = pd.DataFrame(data, columns=['title', 'comment', 'link'])

df.to_pickle('naverComment.pk')

driver.close()