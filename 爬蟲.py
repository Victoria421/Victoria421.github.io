from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from opencc import OpenCC
import time
import re
from datetime import datetime

# 🔍 抓取微博娛樂熱搜前十
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
    cc = OpenCC('s2t')
    hotsearch_list = []

    for tr in rows:
        a = tr.select_one("td.td-02 a")
        if a:
            text = cc.convert(a.get_text(strip=True))
            link = "https://s.weibo.com" + a['href']
            hotsearch_list.append((text, link))

    return hotsearch_list

# 🔧 產生 <ol> HTML 列表
def generate_html(hotsearch_list):
    html = '<ol style="text-align:left; padding-left:20px;">\n'
    for text, link in hotsearch_list:
        html += f'  <li><a href="{link}" target="_blank">{text}</a></li>\n'
    html += '</ol>'
    return html

# 🔧 更新指定 HTML 區塊
def update_html_file(html_path, list_html, update_time):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替換 weibo-hotsearch-list
    list_pattern = re.compile(
        r'(<div[^>]+id=["\']weibo-hotsearch-list["\'][^>]*>)(.*?)(</div>)',
        re.DOTALL
    )
    content = list_pattern.sub(r'\1' + list_html + r'\3', content)

    # 替換更新時間
    time_pattern = re.compile(
        r'(<p[^>]+id=["\']last-updated-time["\'][^>]*>)(.*?)(</p>)',
        re.DOTALL
    )
    time_html = f'<p id="last-updated-time">資料更新時間：{update_time}</p>'
    content = time_pattern.sub(time_html, content)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 🚀 主程式
if __name__ == "__main__":
    hotsearch = fetch_weibo_ent_hotsearch()
    if hotsearch:
        list_html = generate_html(hotsearch)
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        update_html_file("elements.html", list_html, update_time)
        print("✅ 熱搜與時間更新完成")
    else:
        print("❌ 抓取失敗")
