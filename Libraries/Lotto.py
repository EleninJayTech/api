class Lotto:
    @classmethod
    def winning_number(cls, target_round: int):
        """

        :param target_round:
        :return:
        """
        api = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}'.format(target_round)
        return api
