from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from auth import authenticate_user, create_token, verify_token
from coingecko import CoinGeckoAPI

app = FastAPI()
api = CoinGeckoAPI()

# ----------------------
# Authentication Models
# ----------------------
class LoginRequest(BaseModel):
    username: str
    password: str

# ----------------------
# Authentication Endpoint
# ----------------------
@app.post("/auth/login")
def login(data: LoginRequest):
    if not authenticate_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token({"sub": data.username})
    return {"access_token": token, "token_type": "bearer"}


# ----------------------
# Protected Endpoints
# ----------------------
@app.get("/coins")
def list_coins(page_num: int = 1, per_page: int = 10, user=Depends(verify_token)):
    coins = api.list_coins()
    start = (page_num - 1) * per_page
    end = start + per_page
    return coins[start:end]


@app.get("/categories")
def list_categories(user=Depends(verify_token)):
    return api.list_categories()


@app.get("/coins/market")
def market_data(
    coin_id: str = None,
    category: str = None,
    page_num: int = 1,
    per_page: int = 10,
    user=Depends(verify_token)
):
    data = api.get_market_data(coin_id, category)

    # pagination applied to both INR and CAD results
    for curr in ["inr", "cad"]:
        items = data[curr]
        start = (page_num - 1) * per_page
        end = start + per_page
        data[curr] = items[start:end]

    return data
