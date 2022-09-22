class Lotto:
    @classmethod
    def save_winning_number(cls):
        """
        python -c 'from batch import Lotto; Lotto.save_winning_number()'
        :return:
        """
        from Libraries.Lotto_api import LottoApi
        api_url = LottoApi.winning_number()
        print(api_url)
        return api_url
