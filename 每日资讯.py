import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

"""update : 

    remark: 
    加入了对志愿者官网的志愿服务活动的爬取功能，显示不可报名的意思并不代表志愿者满了，大概率是还未开始招募
    因为我只选了前五项，而前五项的一一般都过早了。想调整前几项可以往下自己改，都注释了。
    
    对于这种没开始报名的需要自己飞书联系负责人，问问咋报名，一般都是他们学院的公众号，或者他们学院的志愿者大群
    需要自己去问下
    
    ——————————————————————————————————
    by Zhaoyang Liang
    budongjishubu@gmail.com
    Latested update : Mar. 1 2025
    
"""

"""clea

    该程序用于爬取教务(新加入)计网学院与金融学院的每日的更新内容，没有则输出最新的三条
    ∆ (经过多次改版目前已经变成了全部都输出最新更新的前三条内容) 2024.8.9
    输出格式为：【隶属板块】 + 日期 + 标题 + 相对url(最新版本改成了绝对url)

        关于程序任务的完成，将 “[:3]“ 对应的3改成1即为只要最最近更新的，将对应模块注释掉程序将只完成显示当日更新的内容，
    但由于金融学院官网更新的频率远远高于计网学院，所以一直当前显示3条是比较合理的，计网则无所谓（而且考虑到计网两个网站每次
    更新的东西几乎一样）但目前经过调试是显示3条是较为合理的选择。

        关于每日自动运行和手动运行，自动运行对不同电脑的环境配置要求不一样，这里不做实现。
    当前程序实现的是每日手动运行可以实时更新

        关于用户UA与cookie，南开大学官网虽然在网安学院官网和部分官网使用的是https协议，但并没有设置相关的限制，
    这里不做用户request类的定制

        关于 name = main 函数 ，比较懒 ，本质上这是四个程序拼起来的，就没改

    ——————————————————————————————————
    by Zhaoyang Liang
    budongjishubu@gmail.com
    Latested update : Aug. 9 2024
    
"""

from datetime import date
from lunarcalendar import Converter, Solar
def print_current_dates():
    # 获取当前日期
    today = date.today()

    # 打印公历日期
    print(f"今天是公历 {today.year} 年 {today.month} 月 {today.day} 日")

    # 将当前日期转换为农历
    solar = Solar(today.year, today.month, today.day)
    lunar = Converter.Solar2Lunar(solar)

    # 判断是否闰月
    if lunar.isleap:
        lunar_month = f"闰{lunar.month}"
    else:
        lunar_month = lunar.month

    # 打印农历日期
    print(f"今天是农历 {lunar.year} 年 {lunar_month} 月 {lunar.day} 日")

# 调用函数
print_current_dates()

print("∆教务处的最新3条消息:")
# 目标URL
url = "https://jwc.nankai.edu.cn/course/tyb/tykc/index.psp"

# 发送请求获取网页内容
response = requests.get(url)
response.encoding = 'utf-8'  # 设置编码避免中文乱码

# 检查请求是否成功
if response.status_code != 200:
    print(f"获取网页内容失败，状态码: {response.status_code}")
    exit()

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 基础URL
base_url = "https://jwc.nankai.edu.cn"

# 初始化一个列表来保存提取的新闻信息
all_news = []

# 定义处理函数，用于提取“通知公告”的内容
def extract_announcement_news(items, section_name):
    for item in items:
        day = item.find('div', class_='d').text.strip()
        month_year = item.find('div', class_='m').text.strip()
        title = item.find('div', class_='con').text.strip()
        link = item.find('a')['href']
        
        # 处理日期格式
        year, month = month_year.split('/')
        date = f"{year}-{month}-{day}"
        full_link = urljoin(base_url, link)
        
        all_news.append({
            'section': section_name,
            'title': title,
            'date': date,
            'link': full_link
        })

# 定义处理函数，用于提取“新闻动态”的内容
def extract_news_without_date(items, section_name):
    for item in items:
        title_tag = item.find('div', class_='t') or item.find('a')
        title = title_tag.text.strip()
        date_tag = item.find('div', class_='d') or item.find('div', class_='m')
        date = date_tag.text.strip().replace('.', '-')
        link = item.find('a')['href']
        full_link = urljoin(base_url, link)
        all_news.append({
            'section': section_name,
            'title': title,
            'date': date,
            'link': full_link
        })

# 提取 "通知公告"
notification_items = soup.select('div.section1 .item')
extract_announcement_news(notification_items, '通知公告')

# 提取 "新闻动态"
news_items = soup.select('div.section2-left-newslist .item')
extract_news_without_date(news_items, '新闻动态')

# 按日期排序并提取最新的10条消息
all_news = sorted(all_news, key=lambda x: x['date'], reverse=True)[:3]

# 打印提取的最新新闻
for news in all_news:
    print(f"【{news['section']}】{news['date']} {news['title']} {news['link']}")


print("∆计算机学院官网最新的3条内容：")


# 获取公告函数
def get_announcements(url, modules):
    response = requests.get(url)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"获取网页内容失败，状态码: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    announcements = []

    def extract_announcements(module_name, module_class):
        announcements_in_module = soup.find_all('a', href=lambda x: x and module_class in x)
        for announcement in announcements_in_module:
            title = announcement.find('span', class_='font-no-newline').text.strip()
            date_str = announcement.find('span', class_='body-home-time').text.strip()
            link = urljoin(url, announcement.get('href'))  # 完整URL
            try:
                if '-' in date_str:
                    if len(date_str) == 5:
                        date = datetime.strptime(date_str, "%m-%d")
                        date = date.replace(year=datetime.now().year)
                    else:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                announcements.append((module_name, date, title, link))
            except Exception as e:
                print(f"日期格式有误: {date_str}")

    for module_name, module_class in modules.items():
        extract_announcements(module_name, module_class)

    return announcements

# 计算机学院
url_cc = 'http://cc.nankai.edu.cn/main.htm'
modules_cc = {
    "最新动态": "c13291",
    "学院公告": "c13292",
    "学生工作通知": "c13293",
    "科研信息": "c13294",
    "本科生教学": "c13295",
    "党团园地": "c13296",
    "研究生招生": "c13297",
    "研究生教学": "c13298",
    "境外交流": "c13299",
}
announcements_cc = get_announcements(url_cc, modules_cc)

# 按日期排序
announcements_cc.sort(key=lambda x: x[1], reverse=True)

# 获取今天的日期
today = datetime.now().date()

# 过滤出今日的更新
today_updates = [item for item in announcements_cc if item[1].date() == today]

# if today_updates:
#     print("计网今日的更新为：")
#     for module_name, date, title, link in today_updates:
#         print(f"【{module_name}】 {date.strftime('%Y-%m-%d')} {title} {link}")
# else:
#     print("计网没有更新，最近的三条公告为：")
for module_name, date, title, link in announcements_cc[:3]:
    print(f"【{module_name}】 {date.strftime('%Y-%m-%d')} {title} {link}")




print("∆网络空间安全学院官网最新的3条内容：")

# 获取公告函数
def get_announcements(url, modules):
    response = requests.get(url)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"获取网页内容失败，状态码: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    announcements = []

    def extract_announcements(module_name, module_class):
        announcements_in_module = soup.find_all('a', href=lambda x: x and module_class in x)
        for announcement in announcements_in_module:
            title = announcement.find('span', class_='font-no-newline').text.strip()
            date_str = announcement.find('span', class_='body-home-time').text.strip()
            link = urljoin(url, announcement.get('href'))  # 完整URL
            try:
                if len(date_str) == 5:  # 处理 MM-DD 格式
                    date = datetime.strptime(date_str, "%m-%d")
                    date = date.replace(year=datetime.now().year)
                elif len(date_str) == 10:  # 处理 YYYY-MM-DD 格式
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    raise ValueError("Unsupported date format")
                announcements.append((module_name, date, title, link))
            except ValueError:
                print(f"日期格式有误: {date_str}")

    for module_name, module_class in modules.items():
        extract_announcements(module_name, module_class)

    return announcements

# 网络空间安全学院
url_cyber = 'https://cyber.nankai.edu.cn'
modules_cyber = {
    "最新动态": "c13342",
    "学院公告": "c13343",
    "学生工作通知": "c13344",
    "科研信息": "c13345",
    "本科生教学": "c13346",
    "党团园地": "c13347",
    "研究生招生": "c13348",
    "研究生教学": "c13349",
    "境外交流": "c13350",
}
announcements_cyber = get_announcements(url_cyber, modules_cyber)

# 按日期排序
announcements_cyber.sort(key=lambda x: x[1], reverse=True)

# 获取今天的日期
today = datetime.now().date()

# 过滤出今日的更新
today_updates = [item for item in announcements_cyber if item[1].date() == today]

# if today_updates:
#     print("网安今日的更新为：")
#     for module_name, date, title, link in today_updates:
#         print(f"【{module_name}】 {date.strftime('%Y-%m-%d')} {title} {link}")
# else:
#     print("网安没有更新，最近的三条公告为：")
for module_name, date, title, link in announcements_cyber[:3]:
    print(f"【{module_name}】 {date.strftime('%Y-%m-%d')} {title} {link}")


print("∆金融学院官网最近更新的3条内容:")

import re

# 基础URL
base_url = "https://finance.nankai.edu.cn"

# 发送请求获取网页内容
response = requests.get(base_url)
response.encoding = 'utf-8'  # 设置编码避免中文乱码

# 检查请求是否成功
if response.status_code != 200:
    raise Exception(f"请求失败，状态码: {response.status_code}")

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 初始化一个列表来保存提取的新闻信息
all_news = []

# 定义处理函数，用于提取每个板块中的内容
def extract_news(items, section_name):
    for item in items:
        day = item.find('div', class_='d')
        month_year = item.find('div', class_='m')
        title = item.find('div', class_='title') or item.find('div', class_='con')
        link = item.find('a')['href']

        if day and month_year and title:
            # 处理日期格式
            date = f"{month_year.text.strip().replace('/', '-')}-{day.text.strip()}"
            full_link = base_url + link
            all_news.append({
                'section': section_name,
                'title': title.text.strip(),
                'date': date,
                'link': full_link
            })

# 针对特殊板块的处理（没有标准结构）
def extract_special_news(items, section_name):
    for item in items:
        date = item.find('div', class_='date')
        title = item.find('div', class_='title') or item.find('div', class_='con')
        link = item.find('a')['href']

        if date and title:
            full_link = base_url + link
            all_news.append({
                'section': section_name,
                'title': title.text.strip(),
                'date': date.text.strip(),
                'link': full_link
            })

# 提取每个板块的新闻
sections = [
    ('学院新闻', soup.find_all('div', class_='section1')[0].find_all('div', class_='item')),
    ('通知公告', soup.find_all('div', class_='section2')[0].find_all('div', class_='item')),
    ('学术活动', soup.find_all('div', class_='section3')[0].find_all('div', class_='item')),
    ('招生工作', soup.find_all('div', class_='section4-con section4-con1')[0].find_all('div', class_='item')),
    ('校友风采', soup.find_all('div', class_='section5-list1')[0].find_all('div', class_='item'))
]

# 处理常规板块
for section_name, items in sections[:-2]:  # 处理前面几个标准结构的板块
    extract_news(items, section_name)

# 处理特殊结构的板块
special_sections = [
    ('学术活动', soup.find_all('div', class_='section3-list-new')[0].find_all('div', class_='item')),
    ('招生工作', soup.find_all('div', class_='section4-con section4-con1')[0].find_all('div', class_='item'))
]

for section_name, items in special_sections:
    extract_special_news(items, section_name)

# 按日期排序并提取最新的10条消息
all_news = sorted(all_news, key=lambda x: x['date'], reverse=True)[:3] #这里改成了3我

# 打印提取的最新新闻
for news in all_news:
    print(f"【{news['section']}】{news['date']} {news['title']} {news['link']}")
    


# 定义目标URL
url = 'https://zyfw.nankai.edu.cn'

# 发送HTTP请求获取网页内容
response = requests.get(url)
response.encoding = response.apparent_encoding  # 自动检测编码

# 解析网页内容
soup = BeautifulSoup(response.text, 'html.parser')

# 查找包含志愿活动的表格
activities_table = soup.find('div', class_='index-part1').find('table')

print("∆志愿服务官网最近更新的5条志愿活动:")

# 设置计数器，最多读取前3条活动
activity_count = 0
for row in activities_table.find_all('tr')[1:]:  # 跳过表头
    if activity_count >= 5:  # 只输出前三条活动
        break

    columns = row.find_all('td')
    if len(columns) > 2:  # 确保这行有足够的列
        activity_name = columns[0].find('a').text.strip()  # 活动名称
        start_time = columns[1].text.strip()  # 活动开始时间
        url_suffix = columns[0].find('a')['href']  # 活动链接
        activity_url = f"https://zyfw.nankai.edu.cn{url_suffix}"  # 完整的活动链接
        # 获取报名信息（判断是否报名）
        sign_up_status = columns[2].text.strip() if columns[2].text.strip() else "未知"
        
        # 即时输出每条活动的信息
        print(f"【志愿活动】{start_time} {sign_up_status} {activity_name}  {activity_url} ")

        # 增加计数器
        activity_count += 1