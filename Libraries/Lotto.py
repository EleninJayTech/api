class Lotto:
    @classmethod
    def winning_number(cls, target_round: int):
        api = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}'.format(target_round)
        return api
