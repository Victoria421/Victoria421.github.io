from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
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
    # 改成有序列表，數字序列，自動靠左
    html_content = '<ol style="text-align:left; padding-left:20px;">\n'
    for text, link in hotsearch_list:
        html_content += f'  <li><a href="{link}" target="_blank">{text}</a></li>\n'
    html_content += '</ol>'
    return html_content


def update_html_file(html_file_path, new_list_html):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 用 id="weibo-hotsearch-list" 區塊做替換
    pattern = re.compile(
        r'(<div[^>]+id=["\']weibo-hotsearch-list["\'][^>]*>)(.*?)(</div>)',
        re.DOTALL
    )

    new_content = pattern.sub(r'\1' + new_list_html + r'\3', content)

    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"已更新 {html_file_path} 中的微博熱搜文娛榜內容。")

if __name__ == "__main__":
    hotsearch_list = fetch_weibo_ent_hotsearch()
    if hotsearch_list:
        new_html = generate_html(hotsearch_list)
        update_html_file("index.html", new_html)
    else:
        print("抓取微博文娛榜前十失敗")
