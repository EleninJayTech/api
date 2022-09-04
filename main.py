from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

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


@app.get("/")
async def read_root(
        user_agent: str | None = Header(default=None)
):
    return {"User-Agent": user_agent}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/db_test")
async def read_db_test():
    from Libraries.Database import Database

    account_type = Database.query_fetch_all("SELECT * FROM account_type")
    return account_type
