import configparser

import cryptocode
import mariadb
import re
from Core.Constants import ROOT_DIR
from Libraries.Utility import path_slash


class Database:
    # 설정 정보 가져 오기
    config = configparser.ConfigParser()

    secure_path = '{}./secure.ini'.format(ROOT_DIR)
    secure_path = path_slash(secure_path)

    config.read(secure_path)
    ENVIRONMENT = config['system']['ENVIRONMENT']
    # encrypt key
    encrypt_key = config['encrypt']['encrypt_key']

    # db 설정
    db_user = config['db']['user']
    db_password = cryptocode.decrypt(config['db']['password'], encrypt_key)
    if ENVIRONMENT == 'development':
        db_password = ''
    db_host = config['db']['host']
    db_port = config['db']['port']
    db_database = config['db']['database']

    db_connect = None

    @classmethod
    def database_connect(cls):
        if cls.db_connect is None:
            try:
                cls.db_connect = mariadb.connect(
                    user=str(cls.db_user),
                    password=str(cls.db_password),
                    host=str(cls.db_host),
                    port=int(cls.db_port),
                    database=str(cls.db_database)
                )
            except mariadb.Error as e:
                print(f"Error connecting to MariaDB Platform: {e}")

        return cls.db_connect

    @classmethod
    def bind(cls, sql, data):
        # 정규 표현식을 컴파일하여 재사용
        pattern = re.compile(r':\w+')
        matches = pattern.findall(sql)

        # 필요한 파라미터 추출
        params = [data[key[1:]] for key in matches]  # ':' 제거 및 데이터 추출
        param_tuple = tuple(params)

        # SQL 쿼리에서 실제로 사용되는 키에 대해서만 문자열 교체
        formatted_sql = sql
        for match in matches:
            key = match[1:]  # ':' 제거
            if key in data:
                formatted_sql = formatted_sql.replace(match, '%s')

        return formatted_sql, param_tuple

    @classmethod
    def bind2(cls, sql, data):
        # 정규 표현식을 사용하여 :로 시작하는 단어 찾기
        pattern = r':\w+'
        matches = re.findall(pattern, sql)
        params = []
        for key in matches:
            key = key.replace(':', '')
            params.append(data[key])
        param_tuple = tuple(params)

        formatted_sql = sql
        for key in data:
            if key in formatted_sql:
                formatted_sql = formatted_sql.replace(f':{key}', '%s')
        return formatted_sql, param_tuple

    @classmethod
    def query_row(cls, sql: str):
        """
        :param sql:
        :return:
        """
        if sql == '':
            return None

        if cls.db_connect is None:
            cls.db_connect = cls.database_connect()

        cursor = cls.db_connect.cursor()
        cursor.execute("{}".format(sql))
        fetch_data = cursor.fetchone()

        cursor.close()
        # cls.db_connect.close()
        # cls.db_connect = None

        return fetch_data

    @classmethod
    def query_fetch_all(cls, sql: str, return_column: bool = False):
        """
        :param sql:
        :param return_column:
        :return:
        """
        fetch_data = []

        if sql == '':
            return fetch_data

        if cls.db_connect is None:
            cls.db_connect = cls.database_connect()

        cursor = cls.db_connect.cursor()
        cursor.execute("{}".format(sql))
        fetch_data = cursor.fetchall()

        if return_column:
            # num_fields = len(cursor.description) # 필드 수
            field_names = [i[0] for i in cursor.description]  # 필드 명 구하기
            new_fetch_data = []
            for data_list in fetch_data:
                new_row = []

                for field_idx, field_data in enumerate(data_list):
                    new_row.append({'{}'.format(field_names[field_idx]): field_data})

                new_fetch_data.append(new_row)
            fetch_data = new_fetch_data

        cursor.close()
        # cls.db_connect.close()
        # cls.db_connect = None

        return fetch_data

    @classmethod
    def query(cls, sql: str, params=None):
        if sql == '':
            return False

        if cls.db_connect is None:
            cls.db_connect = cls.database_connect()

        try:
            cursor = cls.db_connect.cursor()
            cursor.execute(sql, params)
            cls.db_connect.commit()
        except Exception as e:
            print(e)
            return False

        cursor.close()
        return True