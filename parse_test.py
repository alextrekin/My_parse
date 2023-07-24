import time, lxml
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import random

num_page=0
indication = True
parse_page = {}
urls=[]
url_pagination = None

# функция открытия страницы и получения ее кода
def get_sourse_html(url):
    driver = uc.Chrome()
    
    try:
        driver.get(url=url)
        soup = BeautifulSoup(driver.page_source, "lxml")
    except Exception as _ex:
        print (_ex)
    finally:
        time.sleep(random.randint(4,6))
        driver.quit()
        return soup

# функция которая получает список компаний  
def get_item_url(url, soup):
    global num_page
    if (num_page == 0):
        soup = get_sourse_html(url)
        
    items_divs = soup.find_all("h3", class_="company_info")

    if indication is True:
        global urls
        for item in items_divs:
            item_url = item.find("a").get("href")
            urls.append(item_url)
        next_pagination_company(soup)


# функция для обхода списка компаний 
def get_data(file_company):
    with open(file_company) as file:
        urls_list = [url.strip() for url in file.readlines()]
    global num_page
    num_page = 0    
    for url in urls_list:
        global url_pagination
        url_pagination = url
        soup = get_sourse_html(url)
        get_info_company(url,soup)
        
# тут получаем уже все отзывы постранично 
def get_info_company(url, soup):
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
        url_company=url_pagination+f"?page={num_page}"
        soup = get_sourse_html(url_company)
        get_info_company(url_company, soup)
    else:
        num_page = 0
        
# пагинатор для сбора компаний
def next_pagination_company(soup):

    pagination = soup.find("ul", class_="pagination justify-content-center").find("li", class_="page-item next")
    if pagination is not None:
        global num_page
        num_page+=1
        start = 'https://clutch.co/directory/android-application-developers?geona_id=40823'
        url_company=start+f"&page={num_page}"
        soup = get_sourse_html(url_company)
        get_item_url(url_company, soup)
    else:
        num_page = 0
        global indication
        indication = False
        save_company()
                
def save_csv(parse_page):
    df = pd.DataFrame(parse_page)
    df.to_csv("parse.csv", mode='a', index= False , header= False)

def save_company():
    global urls
    with open ("company.txt","w") as file:
        for url in urls: 
            file.write(f"https://clutch.co{url}\n")
    print(len(urls))
    get_data("./company.txt") 
    
            
def main():
    url = 'https://clutch.co/directory/android-application-developers?geona_id=40823'
    soup = None
    get_item_url(url,soup)

if __name__ == "__main__":
    main()
