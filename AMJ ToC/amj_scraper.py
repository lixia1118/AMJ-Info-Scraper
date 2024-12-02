from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import csv
from time import sleep
import random
import os

def setup_driver():
    edge_options = Options()
    
    # 添加 headless 模式的选项
    edge_options.add_argument('--headless')
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--disable-extensions')
    edge_options.add_argument('--disable-software-rasterizer')
    edge_options.add_argument('--ignore-certificate-errors')
    edge_options.add_argument('--window-size=1920,1080')
    edge_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # 添加以下选项来抑制日志
    edge_options.add_argument('--log-level=3')  # 只显示致命错误
    edge_options.add_argument('--silent')
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        service = Service(r"D:\msedgedriver.exe")
        driver = webdriver.Edge(service=service, options=edge_options)
        return driver
    except Exception as e:
        print(f"启动Edge浏览器时出错: {str(e)}")
        print("请确保：")
        print("1. Edge浏览器已正确安装")
        print("2. msedgedriver.exe 版本与Edge浏览器版本匹配")
        print("3. msedgedriver.exe 路径正确")
        raise e

def write_to_csv(articles, file_path, is_new=False):
    mode = 'w' if is_new else 'a'
    with open(file_path, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Volume', 'Issue', 'Year', 'Title', 'Authors', 'DOI', 'Link'])
        if is_new:  # 只在新文件时写入表头
            writer.writeheader()
        writer.writerows(articles)

def get_year_from_volume(volume):
    # 第36卷是1993年，每卷加一年
    return 1993 + (volume - 36)

def scrape_amj_page(volume, issue):
    driver = setup_driver()
    
    try:
        url = f"https://journals.aom.org/toc/amj/{volume}/{issue}"
        print(f"\n正在访问页面: {url}")
        driver.get(url)
        
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "article-meta"))
        )
        
        # 缓慢滚动到页面底部
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 滚动一小段距离
            for i in range(0, last_height, 100):  # 次滚动100像素
                driver.execute_script(f"window.scrollTo(0, {i});")
                sleep(random.uniform(0.1, 0.3))  # 随机延迟0.1-0.3秒
            
            # 等待页面加载
            sleep(random.uniform(1, 2))
            
            # 计算新的滚动高度
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # 如果高度没有变化，说明已经到达底部
            if new_height == last_height:
                break
            last_height = new_height
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = []
        
        article_elements = soup.find_all('div', class_='article-meta')
        print(f"找到 {len(article_elements)} 个文章元素")
        
        for article in article_elements:
            try:
                title_link = article.find('h5', class_='issue-item__title').find('a')
                title = title_link.text.strip()
                doi = title_link['href'].replace('/doi/', '')
                
                # 根据卷号计算年份
                year = get_year_from_volume(volume)
                
                authors_list = article.find('ul', class_='rlist--inline loa')
                if authors_list:
                    authors = [author.find('span').text.strip() for author in authors_list.find_all('li')]
                    authors = '; '.join(authors)
                else:
                    authors = ''
                
                link = f"https://journals.aom.org{title_link['href']}"
                
                articles.append({
                    'Volume': volume,
                    'Issue': issue,
                    'Year': year,
                    'Title': title,
                    'Authors': authors,
                    'DOI': doi,
                    'Link': link
                })
                
            except Exception as e:
                print(f"解析文章时出错: {str(e)}")
                continue
        
        return articles
        
    except Exception as e:
        print(f"爬取 Volume {volume}, Issue {issue} 时出错: {str(e)}")
        return []
    
    finally:
        driver.quit()

def main():
    output_file = 'AMJ ToC/amj_articles.csv'
    total_articles = 0
    
    # 检查是否需要创建新文件
    is_new_file = not os.path.exists(output_file)
    
    try:
        for volume in range(15, 18):
            for issue in range(1, 7):
                print(f"\n正在爬取第 {volume} 卷第 {issue} 期...")
                articles = scrape_amj_page(volume, issue)
                
                if articles:
                    write_to_csv(articles, output_file, is_new=(is_new_file and total_articles == 0))
                    total_articles += len(articles)
                    print(f"本期成功爬取 {len(articles)} 篇文章")
                    print(f"当前总计已爬取 {total_articles} 篇文章")
                    
                    latest_article = articles[-1]
                    print("\n最新爬取文章信息：")
                    print(f"年份：{latest_article['Year']}")
                    print(f"标题：{latest_article['Title']}")
                    print(f"作者：{latest_article['Authors']}")
                    print(f"DOI：{latest_article['DOI']}")
                
                # 增加随机延迟到3-6秒
                sleep_time = random.uniform(1, 3)
                print(f"等待 {sleep_time:.1f} 秒...")
                sleep(sleep_time)
        
        print(f"\n爬取完成！共爬取 {total_articles} 篇文章")
        print(f"数据已保存到 {output_file}")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        
if __name__ == "__main__":
    main() 