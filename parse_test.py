import time, lxml
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
# from urllib.parse import unquote
# import random
num_page=0
indication = False
# функция открытия страницы и получения ее кода
def get_sourse_html(url):
    global driver 
    driver = uc.Chrome()
    # driver.maximize_window()
    
    try:
        driver.get(url=url)
        time.sleep(10)
        with open ("source.html","w") as file:
            file.write(driver.page_source)
    except Exception as _ex:
        print (_ex)
    # finally:
    #     driver.close()

# функция которая получает список компаний  
def get_item_url(url):
    get_sourse_html(url)
        
    soup = BeautifulSoup(driver.page_source, "lxml")
    items_divs = soup.find_all("h3", class_="company_info")

    urls=[]
    for item in items_divs:
        item_url = item.find("a").get("href")
        urls.append(item_url)

    with open ("company.txt","w") as file:
        for url in urls: 
            file.write(f"https://clutch.co{url}\n")
    if indication is True:
        get_data("./company.txt")

# функция для обхода списка компаний 
def get_data(file_company):
    with open(file_company) as file:
        urls_list = [url.strip() for url in file.readlines()]
    global num_page
    num_page = 0    
    for url in urls_list:
        time.sleep(10)
        get_sourse_html(url)
        time.sleep(10)
        get_info_company(url)
        
# тут получаем уже все отзывы постранично 
def get_info_company(url):
    soup = BeautifulSoup(driver.page_source, "lxml")
    # with open ("./info_company.html") as file:
    #     src = file.read()
    # soup = BeautifulSoup(src, "lxml")
    # получаю имя и фамилию
    try:
        items_names=[]
        item_name = soup.find_all("div", class_="reviewer_card--name")
        for item in item_name:
            items_names.append(item.get_text())
        items_names.pop(0)
    except Exception as _ex:
        item_name = None
    # получаю должность и имя компании
    try:
        items_positions=[]
        item_position = soup.find_all("div", class_="reviewer_position")
        for position in item_position:
            items_positions.append(position.get_text())
        items_positions.pop(0)
    except Exception as _ex:
        item_position = None
        # получаю индустрию и город
    try:
        items_industrys=[]
        items_city=[]
        start = 5
        item_industry = soup.find_all("span", class_="reviewer_list__details-title sg-text__title")
        while start<54:
            items_industrys.append(str(item_industry[start])[58:-7])
            start+=1
            items_city.append(str(item_industry[start])[58:-7])
            start+=4
    except Exception as _ex:
        item_industry = None

    # получаю стоимость проекта  
    try:
        items_price=[]
        item_price = soup.find_all("ul", class_="data--list")
        for price in item_price:
            i = 'icon_tag"></span>\n'
            start = str(price).find(i)
            stop = str(price)[start:].find('</li>')+start
            items_price.append(str(price)[start+len(i):stop].lstrip().rstrip())
        items_price.pop(0)
    except Exception as _ex:
        item_price = None
        
    # получаю описание проекта  
    try:
        items_summary=[]
        item_summary = soup.find_all("div", class_="profile-review__summary mobile_hide")
        for summary in item_summary:
            items_summary.append(summary.get_text())
        items_summary.pop(0)
    except Exception as _ex:
        item_summary = None
        
    # получаю год комментария  
    try:
        items_year=[]
        item_years = soup.find_all("div", class_="profile-review__date")
        for year in item_years:
            items_year.append(year.get_text())
        items_year.pop(0)
    except Exception as _ex:
        item_years = None
    items_urls=[]    
    items_urls=[url]*len(items_year)
    parse_page = {"FIO":items_names,
                  "Rewiewer":items_positions,
                  "Industry":items_industrys,
                  "Price":items_price,
                  "Summary":items_summary,
                  "State":items_city,
                  "Year":items_year,
                  "Link":items_urls}
    save_csv(parse_page)
    next_pagination(soup, url)

#функция проверки следующей страницы комментариев
def next_pagination(soup, url):

    pagination = soup.find("ul", class_="sg-pagination").find("button", {"aria-label":"Reviews Pagination Next"})
    if pagination is not None:
        global num_page
        num_page+=1
        url_company=url+f"?page={num_page}"
        driver.close()
        get_sourse_html(url_company)
        get_info_company(url_company)
    else:
        num_page = 0
        driver.quit()
# пагинатор для сбора компаний
def next_pagination_company(soup, url):

    pagination = soup.find("ul", class_="pagination justify-content-center").find("li", class_="page-item next")
    if pagination is not None:
        global num_page
        num_page+=1
        url_company=url+f"&page={num_page}"
        get_sourse_html(url_company)
        get_item_url(url_company)
    else:
        num_page = 0
        global indication
        indication = True
        # driver.quit()
                
def save_csv(parse_page):
    df = pd.DataFrame(parse_page)
    df.to_csv("parse.csv")
    
            
def main():
    url = 'https://clutch.co/directory/android-application-developers?geona_id=40823'
    get_item_url(url)
    # get_info_company()

if __name__ == "__main__":
    main()
