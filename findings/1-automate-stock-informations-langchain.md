# LangChain 및 Gemini 3 Pro 기반 주식 정보 분석 파이프라인

미국 주식 개별 종목에 대하여 **Tiingo API**로 데이터를 수집하고, **Gemini 3 Pro (via LangChain)**를 활용하여 뉴스를 한국어로 번역하는 자동화 파이프라인 구현 방안입니다.

## 1. 환경 설정 (Setup)

`langchain` 생태계와 Google의 Gemini 모델을 사용하기 위한 `langchain-google-genai`, 그리고 `tiingo` 라이브러리를 설치합니다.

```bash
pip install langchain langchain-google-genai tiingo pandas
```

## 2. Tiingo API 데이터 수집 모듈

Tiingo의 Python Client를 사용하여 펀더멘털 데이터와 뉴스를 조회합니다.

### 2.1 Tiingo Client 초기화

```python
from tiingo import TiingoClient
import os

# API 키 설정 (가급적 환경 변수 사용)
config = {
    'session': True,
    'api_key': os.getenv("TIINGO_API_KEY", "YOUR_TIINGO_API_KEY") 
}
client = TiingoClient(config)
```

### 2.2 펀더멘털 데이터 (Fundamental Data)

Tiingo의 `get_fundamentals_daily` 함수를 활용합니다.
요청하신 지표(PER, EPS, PEG, EV/EBITDA, FCF, ROE, ROA) 중 일부는 Daily Endpoint에서, 일부는 재무제표(Statements) 데이터에서 산출해야 할 수 있습니다.

```python
def get_stock_fundamentals(ticker: str):
    """
    Tiingo API를 통해 주식의 주요 펀더멘털 지표를 조회합니다.
    """
    try:
        # 데일리 펀더멘털 데이터 조회 (최신 기준)
        # startDate를 지정하여 데이터프레임으로 받습니다.
        df = client.get_fundamentals_daily(ticker, startDate='2025-01-01', asDataFrame=True)
        
        if df.empty:
            return None
        
        latest = df.iloc[-1]
        
        # 데이터 매핑 (Tiingo API 응답 필드명 기준)
        # 지표가 없을 경우 None 처리
        data = {
            "Symbol": ticker,
            "Date": latest.get('date'),
            "PER": latest.get('peRatio'),
            "PEG": latest.get('pegRatio'),
            "EPS": latest.get('eps'), # Trailing EPS
            "EV/EBITDA": latest.get('enterpriseValue') / latest.get('ebitda') if latest.get('ebitda') else None,
            # ROE, ROA 등은 daily 필드에 없을 수 있어 원천 재무제표 API 사용 필요 가능성 있음
            # 편의상 daily endpoint에 제공되는 필드가 있다면 사용하거나, 없으면 계산 로직 추가 필요
            "FCF": latest.get('freeCashFlow'), 
            "ROE": latest.get('roe'),
            "ROA": latest.get('roa')
        }
        return data
    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")
        return None
```

### 2.3 뉴스 데이터 (News Data)

```python
def get_stock_news(ticker: str, limit=3):
    """Tiingo에서 해당 종목의 최신 영문 뉴스를 가져옵니다."""
    try:
        # 영어 뉴스만 필터링하거나, 전체를 가져올 수 있습니다.
        news = client.get_news(tickers=[ticker], limit=limit)
        return news
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []
```

## 3. LangChain & Gemini 3 Pro 파이프라인

LangChain을 사용하여 LLM(Gemini 3 Pro)과 연결하고, 뉴스 번역 작업을 수행합니다.

### 3.1 모델 및 프롬프트 설정

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Gemini 3 Pro 모델 설정
# GOOGLE_API_KEY 환경 변수가 설정되어 있어야 합니다.
llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro",
    temperature=0.1,
    convert_system_message_to_human=True # Google 모델 특성에 따른 옵션 필요시 사용
)

# 번역 프롬프트
translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 금융 번역가입니다. 아래 제공되는 금융 뉴스 요약을 한국어로 자연스럽고 정확하게 번역하세요."),
    ("user", "제목: {title}\n내용: {description}")
])

# LCEL(Language Chain Expression Language)로 체인 구성
translate_chain = translate_prompt | llm | StrOutputParser()
```

### 3.2 통합 분석기 (Analyze Pipeline)

```python
class GeminiStockAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
    
    def run(self):
        print(f"Analyzing {self.ticker} with Gemini 3 Pro...")
        
        # 1. 펀더멘털 데이터 수집
        fundamentals = get_stock_fundamentals(self.ticker)
        
        # 2. 뉴스 수집 및 번역
        raw_news = get_stock_news(self.ticker, limit=3)
        processed_news = []
        
        print("Translating news...")
        for article in raw_news:
            # LangChain을 통한 번역 수행
            korean_summary = translate_chain.invoke({
                "title": article['title'],
                "description": article['description']
            })
            
            processed_news.append({
                "published_date": article['publishedDate'],
                "original_title": article['title'],
                "korean_summary": korean_summary,
                "url": article['url']
            })
            
        return {
            "fundamentals": fundamentals,
            "news": processed_news
        }
```

## 4. 실행 스크립트 예시

```python
if __name__ == "__main__":
    # 사용 예시
    analyzer = GeminiStockAnalyzer("TSLA") # 테슬라 분석
    result = analyzer.run()
    
    # 결과 출력
    if result['fundamentals']:
        print(f"\n[{result['fundamentals']['Symbol']}] Fundamental Snapshot")
        print(f"PER: {result['fundamentals']['PER']}")
        print(f"ROE: {result['fundamentals']['ROE']}")
        print(f"EV/EBITDA: {result['fundamentals']['EV/EBITDA']}")
    
    print("\n[Latest News (Korean Translated)]")
    for news in result['news']:
        print(f"- {news['korean_summary']}")
        print(f"  (Source: {news['url']})\n")
```

## 5. 요약 및 확장 포인트

1.  **모델 변경**: `ChatGoogleGenerativeAI`를 사용하여 **Gemini 3 Pro** 모델을 지정함으로써, 고성능의 다국어 처리 및 금융 문맥 이해 능력을 활용할 수 있습니다.
2.  **데이터 무결성**: Tiingo API는 금융 데이터에 특화되어 있으므로, 데이터가 없을 경우(`None`)에 대한 예외 처리가 중요합니다.
3.  **확장성**: `StockAnalyzer` 클래스를 확장하여 LangChain Agent Tool로 등록하면, "테슬라 PER 알려주고 뉴스 요약해줘"와 같은 챗봇 형태로 쉽게 발전시킬 수 있습니다.
