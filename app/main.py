from fastapi import FastAPI
from app.api.v1.prices import router as prices_router

app = FastAPI()

app.include_router(prices_router, prefix="/api", tags=["Prices"])

"""
docker run -d --name simple_sol_pgs \
  -p 5435:5432 \
  -e POSTGRES_PASSWORD=1111 \
  -e POSTGRES_DB=sql_base \
  -v simple_sol_pgdata:/var/lib/postgresql \
  postgres:18-alpine3.23


curl --request GET \
  --url https://test.deribit.com/api/v2/public/get_index_price
{"jsonrpc":"2.0","id":1,"method":"public/get_index_price","params":{"index_name":"btc_usd"}}  

curl --request GET \
  --url "https://test.deribit.com/api/v2/public/get_index_price?index_name=btc_usd"
  
uvicorn app.main:app --reload

"""
