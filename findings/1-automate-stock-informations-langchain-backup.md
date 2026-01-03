# LangChain 기반 주식 정보 분석 파이프라인 구축 방안

미국 주식 개별 종목에 대하여 뉴스 번역 및 펀더멘털 데이터를 조회하는 자동화 파이프라인 구현 방안입니다.

## 1. 환경 설정 (Setup)

먼저 필요한 라이브러리를 설치합니다. `langchain` 생태계와 `tiingo` 공식 파이썬 라이브러리를 사용합니다.

```bash
pip install langchain langchain-openai tiingo pandas
```

## 2. Tiingo API 데이터 수집 모듈 구현

Tiingo API를 사용하여 펀더멘털 데이터와 뉴스를 가져오는 함수를 작성합니다.

### 2.1 Tiingo Client 설정

```python
from tiingo import TiingoClient

# API 키 설정 (환경 변수 사용 권장)
config = {
    'session': True,
    'api_key': "YOUR_TIINGO_API_KEY"
}
client = TiingoClient(config)
```

### 2.2 펀더멘털 데이터 조회 함수

Tiingo의 Daily Fundamentals API를 사용하면 PER, PEG 등의 지표를 얻을 수 있으며, 재무제표 API를 통해 ROE, ROA 등을 계산하거나 조회할 수 있습니다. 여기서는 Daily Fundamentals 엔드포인트를 주로 활용하는 예시입니다.

```python
import pandas as pd

def get_stock_fundamentals(ticker: str):
    """
    Tiingo API를 통해 주식의 주요 펀더멘털 지표를 조회합니다.
    대상: PER, EPS, PEG, EV/EBITDA, FCF, ROE, ROA
    """
    try:
        # 데일리 펀더멘털 데이터 조회 (최신 기준)
        fundamentals = client.get_fundamentals_daily(ticker, startDate='2023-01-01', asDataFrame=True)
        
        if fundamentals.empty:
            return None
        
        latest = fundamentals.iloc[-1]
        
        # Tiingo 제공 컬럼 매핑 (API 응답 구조에 따라 키값 조정 필요 가능성 있음)
        # 일반적인 키값 예시: peRatio, pegRatio, eps, enterpriseValue, ebitda 등
        # FCF, ROE, ROA 등은 Tiingo 데이터 명세에 따라 필드명이 다를 수 있으므로 확인 필요
        
        data = {
            "Symbol": ticker,
            "Date": latest.get('date'),
            "PER": latest.get('peRatio'),
            "EPS": latest.get('eps'), # 혹은 statements API 필요 가능성
            "PEG": latest.get('pegRatio'),
            "EV/EBITDA": latest.get('enterpriseValue') / latest.get('ebitda') if latest.get('ebitda') else None,
            # 아래 지표들은 daily endpoint에 없을 경우 statements endpoint 활용 필요
            "FCF": latest.get('freeCashFlow'), # 예시 키
            "ROE": latest.get('roe'), 
            "ROA": latest.get('roa')
        }
        return data
    except Exception as e:
        print(f"Error fetching fundamentals: {e}")
        return None
```

*참고: Tiingo의 데이터 필드는 구독 플랜이나 엔드포인트에 따라 상이할 수 있습니다. 위 코드는 개념적 구현이며 실제 필드명(`peRatio` 등) 확인이 필요합니다.*

### 2.3 뉴스 조회 함수

```python
def get_stock_news(ticker: str, limit=3):
    """Tiingo에서 관련 뉴스를 가져옵니다."""
    try:
        news = client.get_news(tickers=[ticker], limit=limit)
        return news
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
```

## 3. LangChain 기반 번역 및 파이프라인 구성

LangChain을 사용하여 가져온 영문 뉴스를 한국어로 번역하고, 전체 흐름을 제어합니다.

### 3.1 번역 Chain 설정

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LLM 초기화 (API Key 필요)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 프롬프트 정의
translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a specialized financial translator. Translate the following financial news summary into natural Korean."),
    ("user", "Title: {title}\nDescription: {description}")
])

# Chain 구성
translate_chain = translate_prompt | llm | StrOutputParser()
```

### 3.2 전체 파이프라인 클래스

데이터 수집과 처리를 위한 실행기입니다.

```python
class StockAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
    
    def run(self):
        print(f"Analyzing {self.ticker}...")
        
        # 1. 펀더멘털 데이터 조회
        fundamentals = get_stock_fundamentals(self.ticker)
        print(f"Fundamentals: {fundamentals}")
        
        # 2. 뉴스 조회 및 번역
        raw_news = get_stock_news(self.ticker)
        processed_news = []
        
        for article in raw_news:
            # LangChain을 통한 번역 실행
            korean_summary = translate_chain.invoke({
                "title": article['title'],
                "description": article['description']
            })
            
            processed_news.append({
                "origin_date": article['publishedDate'],
                "origin_title": article['title'],
                "kr_summary": korean_summary,
                "url": article['url']
            })
            
        return {
            "fundamentals": fundamentals,
            "news": processed_news
        }
```

## 4. 실행 예시

```python
if __name__ == "__main__":
    analyzer = StockAnalyzer("AAPL")
    result = analyzer.run()
    
    print("\n=== Analysis Report ===")
    print(f"PER: {result['fundamentals']['PER']}")
    print(f"ROE: {result['fundamentals']['ROE']}")
    
    print("\n=== Latest News ===")
    for news in result['news']:
        print(f"- {news['kr_summary']} ({news['url']})")
```

## 5. 요약

1.  **TiingoClient**를 활용하여 금융 데이터와 뉴스를 안정적으로 수집합니다.
2.  **LangChain (Dictionary Input)** 구조를 활용하여 뉴스 제목과 내용을 LLM에 전달하고 번역 결과를 받습니다.
3.  이 구조는 추후 LangChain의 **Agents** 기능을 도입하여, "애플의 현재 PER이 얼마고 최근 뉴스는 어때?"와 같은 자연어 질문에 답하는 챗봇으로 확장하기 용이합니다.
