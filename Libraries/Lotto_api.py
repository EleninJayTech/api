import requests

class LottoApi:
    @classmethod
    def get_winning_number(cls, target_round=1):
        api_url = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}'.format(target_round)
        return_data = requests.get(api_url)
        return return_data.json()