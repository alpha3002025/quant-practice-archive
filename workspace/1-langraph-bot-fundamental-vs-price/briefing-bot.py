import keyring
import pandas as pd
import requests
import json

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tiingo import TiingoClient

api_key_gemini = keyring.get_password("gemini_quant_automation", "noriskfullpush")
api_key_claude = keyring.get_password("claude_quant_automation", "noriskfullpush")
api_key_tiingo = keyring.get_password("tiingo", "noriskfullpush")


tiingo_config = {}
tiingo_config['session'] = True
tiingo_config['api_key'] = api_key_tiingo
client = TiingoClient(tiingo_config)


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


def get_tiingo_stock_news_with_api(ticker: str, api_key: str, limit=3):
    try:
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }
        # Tiingo News API는 startDate 파라미터를 받을 수 있음
        params = {
            "tickers": ticker,
            "limit": limit,
            "startDate": "2024-01-01" # 최근 1년치 중 최신순
        }
        
        url = "https://api.tiingo.com/tiingo/news"
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching news for {ticker}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []


search_ticker = "AAPL"

### (1) 펀더멘탈 조회 (주석 처리됨)
# fundamental_data = get_stock_fundamentals(search_ticker)
# print(json.dumps(fundamental_data, indent=2, default=str))

### (2) 뉴스 조회
print(f"Fetching news for {search_ticker} from Tiingo...")
news_data = get_tiingo_stock_news_with_api(search_ticker, api_key=api_key_tiingo, limit=3)
# print(json.dumps(news_data, indent=2, default=str))


print("\n" + "="*50 + "\n[Gemini News Briefing]\n" + "="*50)

from langchain_community.document_loaders import WebBaseLoader

### url 에 해당하는 각 기사들에 대한 기사 본문 가져오기 (스크래핑)
print("Fetching full article contents...")
for article in news_data:
    url = article.get('url')
    if not url:
        continue
        
    try:
        # WebBaseLoader를 사용하여 기사 본문 스크래핑
        loader = WebBaseLoader(url)
        # 봇 차단 방지용 헤더
        loader.requests_kwargs = {'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}}
        
        docs = loader.load()
        full_content = "\n\n".join([d.page_content for d in docs])
        
        # 너무 긴 텍스트는 잘라낼 수도 있지만 일단 저장
        article['full_content'] = full_content
        print(f"  - Loaded content for: {article.get('title')[:30]}...")
        
    except Exception as e:
        print(f"  - Failed to load content for {url}: {e}")
        article['full_content'] = "" # 실패 시 빈 문자열

# (3) Gemini 뉴스 분석 프롬프트 (Raw Text)
prompt_template_str = """
당신은 전문적인 추세추종 및 퀀트 투자자(Quantitative Investor)를 위한 AI 금융 비서입니다.
제공된 뉴스 기사의 메타데이터(제목, 설명, URL)를 바탕으로 다음 형식에 맞춰 브리핑 보고서를 작성하세요.

**작성 형식:**
기사. {{번역된 한글 제목}}
- 원문 제목 : {{title}}
- URL : {{url}}
- 출처 : {{source}}
- 발행일 : {{publishedDate}}

[요약 및 투자 인사이트]
{{url}} 의 내용을 분석하여 해당 기사의 내용을 한글로 번역하고, 전문적인 추세추종 및 퀀트 투자자 입장에서 5~10줄 내외의 통찰력 있는 요약문을 작성하세요.단순 사실 나열이 아닌, 이 뉴스가 시장 심리(Sentiment), 변동성(Volatility), 또는 특정 섹터/종목의 추세에 미칠 수 있는 영향을 중심으로 분석해야 합니다.
---

**입력 데이터:**
- 제목: {title}
- URL: {url}
- 내용(Description): {description}
- 출처: {source}
- 발행일: {publishedDate}
"""

import time

# Claude (Anthropic) 모델 설정
# claude-3-5-sonnet-20241022 (Claude 3.5 Sonnet New Version)
print(f"Initializing Claude model: claude-sonnet-4-20250514...")

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=api_key_claude,
    temperature=0.1
)

# 체인 생성
prompt = ChatPromptTemplate.from_template(prompt_template_str)
chain = prompt | llm | StrOutputParser()

# 뉴스별 분석 수행
print(f"Analyzing {len(news_data)} articles...")
for article in news_data:
    try:
        # full_content가 있으면 그것을 description으로 사용, 없으면 기존 description 사용
        # Claude는 토큰 컨텍스트가 200k로 매우 크므로 넉넉하게 사용 가능 (예: 10000자)
        content_to_analyze = article.get('full_content')
        if content_to_analyze:
            content_to_analyze = content_to_analyze[:10000] 
        else:
            content_to_analyze = article.get('description', '')

        input_data = {
            "title": article.get('title', ''),
            "url": article.get('url', ''),
            "description": content_to_analyze,  # 스크래핑된 본문 우선 사용
            "source": article.get('source', 'Unknown'),
            "publishedDate": article.get('publishedDate', '')
        }
        
        result = chain.invoke(input_data)
        print("\n" + result)
        
        # Claude는 Rate Limit이 넉넉하므로 별도 딜레이 불필요 (필요시 추가)
        # time.sleep(1)
        
    except Exception as e:
        print(f"Error processing article: {e}")

