import configparser
import io
import zipfile

import requests
import xmltodict
from fastapi import APIRouter, HTTPException

from Core.Constants import ROOT_DIR
from Libraries.Utility import path_slash

router = APIRouter()


@router.get("/stock")
async def stock():
    from Libraries.Database import Database
    Database.db_database = 'stock'

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
        # data = [{'corp_code': '00430964', 'corp_name': '굿앤엘에스', 'stock_code': None, 'modify_date': '20170630'}]
        for i in range(len(data)):
            corp_code = data[i]['corp_code']
            corp_name = data[i]['corp_name']
            stock_code = data[i]['stock_code']
            if stock_code is None:
                stock_code = ''
            modify_date = data[i]['modify_date']
            SQL = "INSERT INTO corp_code (corp_code, corp_name, stock_code, modify_date) VALUES ('{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE corp_name = '{}', stock_code='{}', modify_date='{}'".format(
                corp_code, corp_name, stock_code, modify_date, corp_name, stock_code, modify_date)
            Database.query(SQL)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error parsing XML data")
    return {"status": "ok"}