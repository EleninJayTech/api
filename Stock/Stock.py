import configparser
import io
import zipfile

import httpx
import requests
import xmltodict
from fastapi import APIRouter, HTTPException

from Core.Constants import ROOT_DIR
from Libraries.Utility import path_slash

router = APIRouter()

@router.get("/stock/corp_code/save")
async def save_corp_code():
    from Libraries.Database import Database
    Database.db_database = 'stock'

    print("save_corp_code start")

    config = configparser.ConfigParser()

    secure_path = '{}./secure.ini'.format(ROOT_DIR)
    secure_path = path_slash(secure_path)

    config.read(secure_path)
    key = config['API_KEY']['OPEN_DART']
    url = "https://opendart.fss.or.kr/api/corpCode.xml"

    params = {"crtfc_key": key}
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
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
            params = {'corp_code':corp_code,'corp_name':corp_name,'stock_code':stock_code,'modify_date':modify_date}
            SQL, params = Database.bind(SQL, params)
            if not Database.query(SQL, params):
                print(f"Query failed: {SQL} with params {params}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error parsing XML data")

    print("save_corp_code end")

    return True


@router.get("/stock/get-price")
async def get_stock_price():
    config = configparser.ConfigParser()

    secure_path = '{}./secure.ini'.format(ROOT_DIR)
    secure_path = path_slash(secure_path)

    config.read(secure_path)
    key = config['API_KEY']['DATA_GO_KR']
    url = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

    params = {
        "serviceKey": key,
        "numOfRows": "1000",
        "pageNo": "1",
        "resultType": "json",
        "basDt": "20231227",
        "beginBasDt": "20231226",
        "endBasDt": "20231228",
        "likeSrtnCd": "016790"
    }
    headers = {"accept": "*/*"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        return response.json()