import keyring
import pandas as pd
import requests

from tiingo import TiingoClient

api_key_tiingo = keyring.get_password("tiingo", "noriskfullpush")
api_key_finnhub = keyring.get_password("finnhub", "noriskfullpush")
config = {}
config['session'] = True
config['api_key'] = api_key_tiingo
client = TiingoClient(config)


def get_stock_fundamentals(ticker: str):
    print(f"Fetching data for {ticker}...")
    try:
        # 1. Daily Data
        daily_list = client.get_fundamentals_daily(ticker, startDate='2024-01-01')
        if not daily_list:
             print("No daily data")
             return None
        
        daily_df = pd.DataFrame(daily_list)
        daily_df['date'] = pd.to_datetime(daily_df['date'])
        daily_latest = daily_df.sort_values('date').iloc[-1]
        
        # 2. Statements Data
        stmt_list = client.get_fundamentals_statements(ticker, startDate='2023-01-01')
        stmt_data = {}
        
        if stmt_list:
            stmt_list.sort(key=lambda x: x['date'], reverse=True)
            latest_stmt = stmt_list[0]
            print(f"Latest statement date: {latest_stmt['date']}")
            
            if 'statementData' in latest_stmt:
                raw_data = latest_stmt['statementData']
                for section in ['incomeStatement', 'cashFlow', 'overview', 'balanceSheet']:
                    for item in raw_data.get(section, []):
                        stmt_data[item.get('dataCode')] = item.get('value')
        
        # 3. Merge
        ev = daily_latest.get('enterpriseVal')
        ebitda = stmt_data.get('ebitda')
        
        data = {
            "Symbol": ticker,
            "Date": daily_latest.get('date'),
            "MarketCap": daily_latest.get('marketCap'),
            "EnterpriseValue": ev,
            "PER": daily_latest.get('peRatio'),
            "PBR": daily_latest.get('pbRatio'),
            "PEG": daily_latest.get('trailingPEG1Y'),
            "EPS": stmt_data.get('epsDiluted'),
            "ROE": stmt_data.get('roe'),
            "ROA": stmt_data.get('roa'),
            "FCF": stmt_data.get('freeCashFlow'),
            "EBITDA": ebitda,
            "EV/EBITDA": (ev / ebitda) if (ev and ebitda) else None
        }
        return data

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_tiingo_stock_news(ticker: str, limit=3):
    """Tiingo에서 해당 종목의 최신 영문 뉴스를 가져옵니다."""
    try:
        # 영어 뉴스만 필터링하거나, 전체를 가져올 수 있습니다.
        news = client.get_news(tickers=[ticker], limit=limit)
        return news
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []


def get_tiingo_stock_news_with_api(ticker: str, api_key: str,limit=3):
    try:
        
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }

        params = {
            "tickers": ticker,
            "limit": limit,
            "startDate": "2026-01-02"
        }
        
        # response = requests.get(f"https://api.tiingo.com/tiingo/news?tickers={ticker}&limit={limit}", headers=headers, params=params)
        
        url = "https://api.tiingo.com/tiingo/news"
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            news_data = response.json()
            return news_data
        else:
            print(f"Error fetching news for {ticker}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []


# def get_finnhub_stock_news_with_api(ticker: str, api_key: str):
#     # 날짜 형식: YYYY-MM-DD
#     # url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2026-01-01&to=2026-01-04&token={api_key}'
#     url = f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from=2026-01-01&to=2026-01-04&token={api_key}'
#     r = requests.get(url)
#     return r.json()


import json
data = get_stock_fundamentals("AAPL")
print(json.dumps(data, indent=2, default=str))

print("===")
news_data = get_tiingo_stock_news_with_api("AAPL", api_key=api_key_tiingo, limit=5)
# news_data = get_finnhub_stock_news_with_api("AAPL", api_key=api_key_finnhub)
print(json.dumps(news_data, indent=2, default=str))

