#爬取Google ap各個地址的經緯度資訊，分別使用BeautifulSoup和Selenium兩個方法處理
#Google Map有爬取次數限制，爬取次數過多會被擋下
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import requests
import pandas as pd
import re


###################載入地址或地名的檔案###################
address_raw = pd.read_csv('address.csv', header=None, encoding='utf_8')
list_address = list(address_raw.iloc[:, 0])

final_list =[]
list_locate_lat =[]
list_locate_lon =[]
address_num = 0 #設定初始完成筆數

method = 2 #選定使用方法1或方法2進行爬蟲

###################方法1：使用BeautifulSoup爬取各個地址的經緯度資訊###################
if method == 1:
    for i in list_address:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        url = 'https://www.google.com.tw/maps/place?q=' + i
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser').prettify()
        try:
            find_latlon = soup.find("\\\",null,[null,null,")
            get_latlon = soup[find_latlon+19:find_latlon+60] #擷取網址中特定位置字串
            lat = re.findall(r'-?\d+\.?\d*', get_latlon)[0] #尋找字串中第1個純數字的部分
            lon = re.findall(r'-?\d+\.?\d*', get_latlon)[1] #尋找字串中第2個純數字的部分
            list_locate_lat.append(lat)
            list_locate_lon.append(lon)
        except: #若查詢不到資料，則經緯度以0表示
            lat = 0
            lon = 0
            list_locate_lat.append(lat)
            list_locate_lon.append(lon)
        address_num += 1 #完成筆數累加
        print(i, lat, lon)
        print('已完成' + str(address_num) + '筆資料') #計算完成筆數
        sleep(3)

        list_combine = pd.DataFrame(zip(list_address, list_locate_lat, list_locate_lon))
        list_combine.columns = ['地址或地名','X','Y']
        output_file = list_combine.to_csv('address_to_wgs84.csv', sep = ',', index=False, encoding='utf_8_sig') #輸出csv


###################方法2：使用Selenium爬取各個地址的經緯度資訊###################
if method == 2:
    for i in list_address:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        url = 'https://www.google.com.tw/maps/place?q=' + i
        resp = requests.get(url)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        ######################Selenium設定#########################
        options = Options()
        options.add_argument('--headless') #啟動無頭模式
        options.add_experimental_option('excludeSwitches', ['enable-logging']) #不輸出logging
        options.add_argument('--log-level=3') #不輸出log
        options.add_argument('--disable-gpu') #windows必須加入此行
        webdriver_path = 'D:\暫存\python實驗室\driver\chromedriver.exe'
        driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
        driver.get(url)
        sleep(3)
        try:
            current_url = driver.current_url
            lat = re.findall(r'-?\d+\.?\d*', current_url)[-3] #尋找倒數第3個純數字的部分
            lon = re.findall(r'-?\d+\.?\d*', current_url)[-1] #尋找倒數第1個純數字的部分
            list_locate_lat.append(lat)
            list_locate_lon.append(lon)
        except: #若查詢不到資料，則經緯度以0表示
            lat = 0
            lon = 0
            list_locate_lat.append(lat)
            list_locate_lon.append(lon)
        address_num += 1 #完成筆數累加
        print(i, lat, lon)
        print('已完成' + str(address_num) + '筆資料') #計算完成筆數

        list_combine = pd.DataFrame(zip(list_address, list_locate_lat, list_locate_lon))
        list_combine.columns = ['地址或地名','lat','lon']
        output_file = list_combine.to_csv('address_to_wgs84.csv', sep = ',', index=False, encoding='utf_8_sig') #輸出csv