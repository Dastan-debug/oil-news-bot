import requests

API_KEY = "1e93c324e138429cb361e3082823dfcc"

def get_oil_news():
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": "crude oil OR oil prices OR OPEC OR oil supply OR Brent OR WTI OR Hormuz OR refinery OR inventory",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 30,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    articles = data.get("articles", [])

    bad_words = [
        "hair", "shampoo", "argan", "bitcoin", "crypto",
        "coupon", "deal", "land rover", "beauty", "skin"
    ]

    oil_keywords = [
        "crude", "oil", "opec", "brent", "wti", "hormuz",
        "tanker", "refinery", "inventory", "sanctions",
        "production", "supply", "terminal", "drone"
    ]

    filtered = []
    seen_titles = set()

    for article in articles:
        title = (article.get("title") or "")
        description = (article.get("description") or "")
        text = f"{title} {description}".lower()

        if any(word in text for word in bad_words):
            continue

        relevance = sum(1 for word in oil_keywords if word in text)
        if relevance < 2:
            continue

        normalized_title = title.strip().lower()
        if normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)

        filtered.append({
            "title": title,
            "source": article.get("source", {}).get("name"),
            "url": article.get("url"),
            "relevance": relevance
        })

    filtered.sort(key=lambda x: x["relevance"], reverse=True)
    return filtered[:10]


def get_oil_news_score():
    articles = get_oil_news()
    score = 0
    reasons = []

    for article in articles:
        title = article["title"].lower()

        # Bullish for oil
        if "drone" in title or "attack" in title or "terminal" in title:
            score += 20
            reasons.append("Supply risk / attack")

        if "hormuz" in title or "strait" in title:
            score += 20
            reasons.append("Hormuz disruption risk")

        if "sanctions" in title:
            score += 15
            reasons.append("Sanctions may reduce supply")

        if (
            "production cut" in title
            or "opec cut" in title
            or "cuts oil output" in title
            or "cuts output" in title
            or "output cut" in title
        ):
            score += 20
            reasons.append("OPEC / production cuts")

        if "refinery outage" in title or "pipeline outage" in title:
            score += 15
            reasons.append("Supply outage")

        if "war" in title or "conflict" in title:
            score += 10
            reasons.append("Geopolitical risk")

        # Bearish for oil
        if "strategic oil release" in title or "emergency oil stocks" in title:
            score -= 15
            reasons.append("Emergency supply release")

        if "inventory build" in title or "stocks rise" in title:
            score -= 20
            reasons.append("Inventory build")

        if "production increase" in title or "opec increase" in title:
            score -= 20
            reasons.append("Production increase")

        if "ceasefire" in title or "peace talks" in title:
            score -= 10
            reasons.append("Lower geopolitical risk")

        if "demand slowdown" in title or "recession" in title:
            score -= 20
            reasons.append("Demand weakness")

    unique_reasons = list(dict.fromkeys(reasons))
    return score, unique_reasons