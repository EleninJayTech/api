import configparser
import io
import zipfile
from datetime import datetime, timedelta
import time
import httpx
import xmltodict
from fastapi import APIRouter, HTTPException

from Core.Constants import ROOT_DIR
from Libraries.Database import Database
from Libraries.Utility import path_slash
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd

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


# 주식 정보를 스크래핑하는 함수
def scrape_stock_info(sosok=0):
    last_page = find_last_page(sosok)
    all_stocks = []
    basDt = datetime.today().strftime("%Y%m%d")

    for page in range(1, last_page + 1):
        print(f"page: {page} / sosok: {sosok}")

        url = f"https://finance.naver.com/sise/sise_market_sum.nhn?sosok={sosok}&page={page}"
        request = urllib.request.urlopen(url)
        html = request.read()
        soup = BeautifulSoup(html, 'html.parser')

        table_rows = soup.find_all("tr", onmouseover="mouseOver(this)")

        time.sleep(1)

        for row in table_rows:
            a_tag = row.find("a")
            stock_code = a_tag['href'].split('=')[-1]
            stock_name = a_tag.text
            td_tags = row.find_all("td")
            current_price = td_tags[2].text.replace(',', '')
            trading_volume = td_tags[9].text.replace(',', '')

            stock = {
                'code': stock_code,
                'name': stock_name,
                'price': current_price,
                'volume': trading_volume
            }
            all_stocks.append(stock)

            SQL = """
                    INSERT INTO stock_daily (basDt, srtnCd, itmsNm, clpr)
                    VALUES (:basDt, :srtnCd, :itmsNm, :clpr)
                    ON DUPLICATE KEY UPDATE basDt=:basDt, srtnCd=:srtnCd, itmsNm=:itmsNm, clpr=:clpr
                """
            params = {'basDt': basDt, 'srtnCd': stock['code'], 'itmsNm': stock['name'], 'clpr': stock['volume']}
            SQL, params = Database.bind(SQL, params)
            if not Database.query(SQL, params):
                print(f"Query failed: {SQL} with params {params}")

        print("all_stocks {}".format(all_stocks))

    return all_stocks


def find_last_page(sosok):
    url = f"https://finance.naver.com/sise/sise_market_sum.nhn?sosok={sosok}"
    request = urllib.request.urlopen(url)
    html = request.read()
    soup = BeautifulSoup(html, 'html.parser')
    last_page = soup.find('td', class_='pgRR').find('a')['href'].split('=')[-1]
    return int(last_page)


@router.get("/stock/today-price")
async def stock_today_price():
    """
    오늘 날짜의 주식 가격(종가) 정보를 가져온다.
    @url https://apiportal.koreainvestment.com/intro
    """
    Database.db_database = 'stock'

    print("stock_today_price start")

    ENVIRONMENT = await read_config('system', 'ENVIRONMENT')
    basDt = datetime.today().strftime("%Y%m%d")
    print(f"basDt : {basDt}")

    # KOSPI 주식 정보 스크래핑
    kospi_stocks = scrape_stock_info(0)

    # KOSDAQ 주식 정보 스크래핑
    kosdaq_stocks = scrape_stock_info(1)

    print("stock_today_price end")

    return True