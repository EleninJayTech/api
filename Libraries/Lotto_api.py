class LottoApi:
    @classmethod
    def winning_number(cls, target_round=1):
        """

        :param target_round:
        :return:
        """
        api = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}'.format(target_round)
        return api
