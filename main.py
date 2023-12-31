from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from Lotto.Lotto import router as lotto_router
from Stock.Stock import router as stock_router
from Stock.Stock import save_corp_code

app = FastAPI(title="My Awesome API", description="This is an awesome API that does amazing things.", version="0.0.1")

origins = [
    "https://eleninjaytech.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로또 라우터
app.include_router(lotto_router)
app.include_router(stock_router)

@app.get("/")
async def read_root(
        user_agent: str | None = Header(default=None)
):
    return {"User-Agent": user_agent}

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    # 스케줄러에 작업 추가
    # scheduler.add_job(save_corp_code, "interval", seconds=60)
    scheduler.add_job(save_corp_code, 'cron', hour=2, minute=0, second=0)
    # 스케줄러 시작
    scheduler.start()

@app.get("/items/{item_id}", summary="요약", description="상세 설명")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/db_test")
async def read_db_test():
    from Libraries.Database import Database
    Database.db_database = 'lotto'
    account_type = Database.query_fetch_all("SELECT * FROM lotto_winning")
    return account_type