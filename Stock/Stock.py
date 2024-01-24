import configparser
import io
import zipfile
from datetime import datetime, timedelta

import httpx
import xmltodict
from fastapi import APIRouter, HTTPException
from selenium.webdriver.common.by import By
from typing import re

from Core.Constants import ROOT_DIR
from Libraries.Database import Database
from Libraries.Utility import path_slash

router = APIRouter()


async def read_config(section, key):
    """
    설정 파일로부터 주어진 섹션의 키에 대한 값을 읽어 반환합니다.
    """
    config = configparser.ConfigParser()
    secure_path = f'{ROOT_DIR}/secure.ini'
    secure_path = path_slash(secure_path)
    config.read(secure_path)
    return config[section][key]


async def fetch_data(url, params):
    """
    비동기적으로 HTTP GET 요청을 보내고 응답을 반환합니다.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response


@router.get("/stock/corp_code/save")
async def save_corp_code():
    """
    (새벽 2시) Open DART API를 이용하여 기업 코드를 저장한다.
    @url https://opendart.fss.or.kr/
    """
    Database.db_database = 'stock'

    print("save_corp_code start")

    key = await read_config('API_KEY', 'OPEN_DART')
    url = "https://opendart.fss.or.kr/api/corpCode.xml"
    params = {"crtfc_key": key}

    try:
        resp = await fetch_data(url, params)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        f = io.BytesIO(resp.content)
        with zipfile.ZipFile(f) as zfile:
            xml = zfile.read("CORPCODE.xml").decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing ZIP file")

    try:
        dict_data = xmltodict.parse(xml)
        data = dict_data['result']['list']
        for i in range(len(data)):
            corp_code = data[i]['corp_code']
            corp_name = data[i]['corp_name']
            stock_code = data[i]['stock_code']
            if stock_code is None:
                stock_code = ''
            modify_date = data[i]['modify_date']

            SQL = """
                INSERT INTO corp_code (corp_code, corp_name, stock_code, modify_date) 
                VALUES (:corp_code, :corp_name, :stock_code, :modify_date) 
                ON DUPLICATE KEY UPDATE corp_name=:corp_name, stock_code=:stock_code, modify_date=:modify_date
            """
            params = {'corp_code': corp_code, 'corp_name': corp_name, 'stock_code': stock_code,
                      'modify_date': modify_date}
            SQL, params = Database.bind(SQL, params)
            if not Database.query(SQL, params):
                print(f"Query failed: {SQL} with params {params}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error parsing XML data")

    print("save_corp_code end")

    return True


@router.get("/stock/get-price")
async def target_stock_price(start_date: str, end_date: str = None):
    '''
    특정 기간 동안의 주식 가격 정보를 가져온다.
    :param start_date: 시작일 (YYYY-MM-DD)
    :param end_date: 종료일 (YYYY-MM-DD)
    :return:
    '''
    if end_date is None:
        end_date = start_date

    start_date = datetime(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10]))
    end_date = datetime(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        await save_stock_price(date_str)
        current_date += timedelta(days=1)

    return True


async def save_stock_price(target_date: str = None):
    """
    (새벽 3시) 공공데이터포털에서 주식 가격 정보를 가져온다.
    항상 2일 전 데이터를 저장한다.
    @url https://www.data.go.kr/data/15094808/openapi.do#/API%20%EB%AA%A9%EB%A1%9D/getStockPriceInfo
    """
    Database.db_database = 'stock'

    print("save_stock_price start")

    key = await read_config('API_KEY', 'DATA_GO_KR')
    url = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

    if target_date is None:
        target_date = (datetime.today() - timedelta(2)).strftime("%Y%m%d")

    print(f"save_stock_price target_date : {target_date}")

    params = {
        "serviceKey": key,
        "numOfRows": "5000",
        "pageNo": "1",
        "resultType": "json",
        "basDt": target_date
    }

    try:
        response = await fetch_data(url, params)
        stock_price_data = response.json()
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))

    total_count = stock_price_data["response"]["body"]["totalCount"]
    if total_count == 0:
        print("No data available for the given date")
        return False

    items = stock_price_data["response"]["body"]["items"]["item"]
    for item in items:
        SQL = """
            INSERT INTO stock_daily (basDt, srtnCd, isinCd, itmsNm, mrktCtg, clpr, vs, fltRt, mkp, hipr, lopr, trqu, trPrc, lstgStCnt, mrktTotAmt)
            VALUES (:basDt, :srtnCd, :isinCd, :itmsNm, :mrktCtg, :clpr, :vs, :fltRt, :mkp, :hipr, :lopr, :trqu, :trPrc, :lstgStCnt, :mrktTotAmt)
            ON DUPLICATE KEY UPDATE isinCd=:isinCd, itmsNm=:itmsNm, mrktCtg=:mrktCtg, clpr=:clpr, vs=:vs, fltRt=:fltRt, mkp=:mkp, hipr=:hipr, lopr=:lopr, trqu=:trqu, trPrc=:trPrc, lstgStCnt=:lstgStCnt, mrktTotAmt=:mrktTotAmt
        """
        params = {
            'basDt': item['basDt'], 'srtnCd': item['srtnCd'], 'isinCd': item['isinCd'], 'itmsNm': item['itmsNm'],
            'mrktCtg': item['mrktCtg'], 'clpr': item['clpr'], 'vs': item['vs'], 'fltRt': item['fltRt'],
            'mkp': item['mkp'], 'hipr': item['hipr'], 'lopr': item['lopr'], 'trqu': item['trqu'],
            'trPrc': item['trPrc'], 'lstgStCnt': item['lstgStCnt'], 'mrktTotAmt': item['mrktTotAmt']
        }
        SQL, params = Database.bind(SQL, params)
        if not Database.query(SQL, params):
            print(f"Query failed: {SQL} with params {params}")

    print("save_stock_price end")

    return True

async def stock_today_price():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service

    import os
    import sys
    import time

    # 디바이스
    current_device = 'pc'
    if os.name == 'posix':
        # 리눅스
        current_device = 'linux'
    elif os.name == 'nt':
        # PC
        current_device = 'pc'

    print('[DEVICE] {}'.format(current_device))

    # 크롬 드라이버 로드
    chromedriver_path = '../chromedriver.exe' if current_device == 'pc' else '/usr/local/bin/chromedriver'
    service = Service(executable_path=chromedriver_path)

    # 크롬 불러오기
    options = webdriver.ChromeOptions()
    if current_device == 'linux':
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
    else:
        # 유저 정보 추가
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")

    # 브라우저 설정
    browser = webdriver.Chrome(
        options= options,
        service=service
    )

    # 초이템 로그인
    url = "https://finance.daum.net"
    browser.get(url)

    # 지연 시간
    delay_term = 1

    stock_code_list = ["089600", "89600"]

    browser_info = []
    browser_info.clear()
    browser.switch_to.window(browser.window_handles[0])
    for stock_code in stock_code_list:
        print('페이지 이동 {}'.format(stock_code))
        time.sleep(delay_term)
        new_link = 'https://finance.daum.net/quotes/A{}'.format(stock_code)
        # 탭 이름
        tab_name = 'stock_code_{}'.format(stock_code)
        # 정보 추가
        browser_info.append(tab_name)
        # 새탭 열기
        script_str = "window.open(\"{}\", \"{}\", 'location=yes');".format(new_link, tab_name)
        browser.execute_script(script_str)
        # 브라우저 정보 순서대로 윈도우 번호 호출
        move_tab_idx = browser_info.index(tab_name) + 1
        # 탭 변경
        browser.switch_to.window(browser.window_handles[move_tab_idx])
        # 상품 있는지 확인
        el_stock_price = browser.find_element(By.CSS_SELECTOR, "#boxSummary > div > span:nth-child(1) > span.currentB > span.numB > strong")
        stock_price_str = el_stock_price.text
        stock_price = int(stock_price_str.replace(",", ""))
        if stock_price is None:
            # 브라우저 정보 삭제
            browser_info.remove(tab_name)
            browser.close()
            break

        # 새탭 브라우저 종료
        for tab_info in browser_info:
            browser.switch_to.window(browser.window_handles[1])
            browser.close()

        # 메인 브라우저 닫기
        browser.switch_to.window(browser.window_handles[0])
        browser.close()
        # 드라이버 종료
        browser.quit()
        sys.exit()