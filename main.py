from fastapi import FastAPI, Request
from news import get_oil_news, get_oil_news_score

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Oil signal bot running"}

@app.get("/news")
def news():
    return {
        "market": "oil",
        "articles": get_oil_news()
    }

@app.get("/news-score")
def news_score():
    score, reasons = get_oil_news_score()
    return {
        "market": "oil",
        "news_score": score,
        "reasons": reasons[:5]
    }

@app.get("/signal")
def signal():
    score, reasons = get_oil_news_score()

    if score >= 30:
        final_signal = "BUY"
    elif score <= -30:
        final_signal = "SELL"
    else:
        final_signal = "NO TRADE"

    return {
        "market": "oil",
        "news_score": score,
        "signal": final_signal,
        "reasons": reasons[:5]
    }

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    tv_signal = data.get("tv_signal")
    price = data.get("price")
    symbol = data.get("symbol")

    news_score, reasons = get_oil_news_score()

    if tv_signal == "BUY" and news_score >= 20:
        final_signal = "BUY"
    elif tv_signal == "SELL" and news_score <= -20:
        final_signal = "SELL"
    else:
        final_signal = "NO TRADE"

    return {
        "market": "oil",
        "symbol": symbol,
        "price": price,
        "tv_signal": tv_signal,
        "news_score": news_score,
        "final_signal": final_signal,
        "reasons": reasons[:5]
    }