from fastapi import APIRouter

router = APIRouter()


@router.get("/lotto/winning/{drwNo}")
async def lotto_winning(drwNo: int):
    from Libraries.Database import Database
    from Libraries.LottoApi import LottoApi
    Database.db_database = 'lotto'
    # [[{'drwNo': 1000}, {'drwNoDate': datetime.date(2022, 1, 29)}, {'totSellamnt': 4294967295}, {'returnValue': 'success'}, {'firstAccumamnt': 4294967295}, {'firstWinamnt': 1246819620}, {'firstPrzwnerCo': 22}, {'bnusNo': 39}, {'drwtNo1': 2}, {'drwtNo2': 8}, {'drwtNo3': 19}, {'drwtNo4': 22}, {'drwtNo5': 32}, {'drwtNo6': 42}]]
    account_type = Database.query_fetch_all("SELECT * FROM lotto_winning WHERE drwNo = {}".format(drwNo), True)
    if not account_type:
        # {'totSellamnt': 118628811000, 'returnValue': 'success', 'drwNoDate': '2022-01-29', 'firstWinamnt': 1246819620, 'drwtNo6': 42, 'drwtNo4': 22, 'firstPrzwnerCo': 22, 'drwtNo5': 32, 'bnusNo': 39, 'firstAccumamnt': 27430031640, 'drwNo': 1000, 'drwtNo2': 8, 'drwtNo3': 19, 'drwtNo1': 2}
        account_type = LottoApi.get_winning_number(drwNo)
    return account_type