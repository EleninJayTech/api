class LottoApi:
    @classmethod
    def winning_number(cls, target_round=1):
        """

        :param target_round:
        :return:
        """
        import requests
        api_url = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}'.format(target_round)
        return_data = requests.get(api_url)
        return return_data.json()
