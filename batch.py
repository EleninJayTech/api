class Lotto:
    @classmethod
    def save_winning_number(cls):
        """
        python -c 'from batch import Lotto; Lotto.save_winning_number()'
        :return:
        """
        from Libraries.Lotto_api import LottoApi

        # todo 최신 저장된 회차 확인
        #  {"totSellamnt":3681782000,"returnValue":"success","drwNoDate":"2002-12-07","firstWinamnt":0,"drwtNo6":40,"drwtNo4":33,"firstPrzwnerCo":0,"drwtNo5":37,"bnusNo":16,"firstAccumamnt":863604600,"drwNo":1,"drwtNo2":23,"drwtNo3":29,"drwtNo1":10}
        #  이후 회차 호출
        #  없는 데이터 {"returnValue":"fail"}
        #  데이터 저장

        target_round = 1

        winning_info = LottoApi.winning_number(target_round)
        return winning_info
