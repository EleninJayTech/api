from Libraries.Lotto_api import LottoApi
from Libraries.Database import Database

Database.db_database = 'lotto'


class Lotto:
    """
    Lotto   : 로또 관련 기능
    """
    @classmethod
    def save_winning_number(cls):
        """
        로또 당첨 번호를 저장한다
        저장된 마지막 회차의 다음 회차를 API 로 호출 하여 당첨 번호를 가져온다
        python3 -c 'from batch import Lotto; Lotto.save_winning_number()'
        :return:
        """
        sql = "SELECT MAX(drwNo) AS drwNo FROM lotto_winning"
        target_round = Database.query_row(sql)[0]
        if target_round is None:
            target_round = 1
        else:
            target_round += 1

        while True:
            winning_info = LottoApi.get_winning_number(target_round)
            if winning_info['returnValue'] == 'fail':
                break

            sql = "INSERT INTO lotto_winning (drwNo, drwNoDate, totSellamnt, returnValue, firstAccumamnt, firstWinamnt, firstPrzwnerCo, bnusNo, drwtNo1, drwtNo2, drwtNo3, drwtNo4, drwtNo5, drwtNo6) VALUES ({}, '{}', {}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(winning_info['drwNo'], winning_info['drwNoDate'], winning_info['totSellamnt'], winning_info['returnValue'], winning_info['firstAccumamnt'], winning_info['firstWinamnt'], winning_info['firstPrzwnerCo'], winning_info['bnusNo'], winning_info['drwtNo1'], winning_info['drwtNo2'], winning_info['drwtNo3'], winning_info['drwtNo4'], winning_info['drwtNo5'], winning_info['drwtNo6'])

            if not Database.query(sql):
                break

            target_round += 1