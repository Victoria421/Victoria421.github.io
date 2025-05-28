# -*- coding: utf-8 -*-
"""
Created on Wed May 28 19:38:44 2025

@author: rosel
"""


from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from opencc import OpenCC

def fetch_weibo_ent_hotsearch():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    url = "https://s.weibo.com/top/summary?cate=ent"
    driver.get(url)
    time.sleep(3)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tbody tr")[:10]

    cc = OpenCC('s2t')  # 簡體轉繁體
    hotsearch_list = []
    for tr in rows:
        a = tr.select_one("td.td-02 a")
        if a:
            text_simplified = a.get_text(strip=True)
            text_traditional = cc.convert(text_simplified)
            link = "https://s.weibo.com" + a['href']
            hotsearch_list.append((text_traditional, link))

    return hotsearch_list

def generate_html(hotsearch_list):
    html_content = '<ol style="text-align:left; padding-left:20px;">\n'
    for text, link in hotsearch_list:
        html_content += f'  <li><a href="{link}" target="_blank">{text}</a></li>\n'
    html_content += '</ol>'
    return html_content

