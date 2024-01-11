import asyncio
import databases
import configparser
import cryptocode

from Core.Constants import ROOT_DIR
from Libraries.Utility import path_slash


class AsyncDatabase:
    config = configparser.ConfigParser()
    secure_path = '{}./secure.ini'.format(ROOT_DIR)
    secure_path = path_slash(secure_path)

    config.read(secure_path)
    encrypt_key = config['encrypt']['encrypt_key']

    # db 설정
    db_user = config['db']['user']
    db_password = cryptocode.decrypt(config['db']['password'], encrypt_key)
    if config['system']['ENVIRONMENT'] == 'development':
        db_password = ''
    db_host = config['db']['host']
    db_port = config['db']['port']
    db_database = config['db']['database']

    DATABASE_URL = f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    database = databases.Database(DATABASE_URL)

    @classmethod
    async def connect(cls):
        await cls.database.connect()

    @classmethod
    async def disconnect(cls):
        await cls.database.disconnect()

    @classmethod
    async def fetch_one(cls, sql: str, values=None):
        if values is None:
            values = {}
        return await cls.database.fetch_one(query=sql, values=values)

    @classmethod
    async def fetch_all(cls, sql: str, values=None):
        if values is None:
            values = {}
        return await cls.database.fetch_all(query=sql, values=values)

    @classmethod
    async def execute(cls, sql: str, values=None):
        if values is None:
            values = {}
        return await cls.database.execute(query=sql, values=values)


# 사용 예제
# async def main():
#     await AsyncDatabase.connect()
#     row = await AsyncDatabase.fetch_one("SELECT * FROM your_table WHERE id = :id", {"id": 1})
#     print(row)
#     await AsyncDatabase.disconnect()

# asyncio.run(main())