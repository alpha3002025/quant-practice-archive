# LangChain 및 Gemini 3 Pro 기반 주식 정보 분석 파이프라인

미국 주식 개별 종목에 대하여 **Tiingo API**로 데이터를 수집하고, **Gemini 3 Pro (via LangChain)**를 활용하여 뉴스를 한국어로 번역하는 자동화 파이프라인 구현 방안입니다.

## 1. 환경 설정 (Setup)

`langchain` 생태계와 Google의 Gemini 모델을 사용하기 위한 `langchain-google-genai`, 그리고 `tiingo` 라이브러리를 설치합니다. (keyring 도 추가)

```bash
pip install langchain langchain-google-genai tiingo pandas keyring
```

tiingo API KEY 설정
```bash
printf "{API Key}" | keyring set tiingo {계정명}
```
<br/>

## 2. Tiingo API 데이터 수집 모듈
Tiingo의 Python Client를 사용하여 펀더멘털 데이터와 뉴스를 조회합니다.<br/>

### 2.1 Tiingo Client 초기화
gemini 의 설명이 구려서 설명 삭제 후 직접 내용 정리함<br/>

```python
import keyring
import pandas as pd

from tiingo import TiingoClient

api_key = keyring.get_password("tiingo", "noriskfullpush")
config = {}
config['session'] = True
config['api_key'] = api_key
client = TiingoClient(config)
```
<br/>

### 2.2 펀더멘털 데이터 (Fundamental Data)

Tiingo의 `get_fundamentals_daily` 함수를 활용합니다.
요청하신 지표(PER, EPS, PEG, EV/EBITDA, FCF, ROE, ROA) 중 일부는 Daily Endpoint에서, 일부는 재무제표(Statements) 데이터에서 산출해야 할 수 있습니다.

```python
def get_stock_fundamentals(ticker: str):
    """
    Tiingo API의 Daily 데이터와 Statements 데이터를 결합하여
    주식의 포괄적인 펀더멘털 지표를 조회합니다.
    """
    try:
        # 1. Daily Data (시가총액, PER, PBR 등 주가 기반 지표)
        daily_list = client.get_fundamentals_daily(ticker, startDate='2024-01-01')
        if not daily_list:
            print(f"No daily fundamental data found for {ticker}")
            return None
            
        daily_df = pd.DataFrame(daily_list)
        daily_df['date'] = pd.to_datetime(daily_df['date'])
        daily_latest = daily_df.sort_values('date').iloc[-1]
        
        # 2. Statements Data (EPS, ROE, FCF 등 재무제표 지표)
        # 최신 재무제표를 얻기 위해 데이터 조회
        stmt_list = client.get_fundamentals_statements(ticker, startDate='2023-01-01')
        stmt_data = {}
        
        if stmt_list:
            # 날짜 기준 내림차순 정렬하여 가장 최근 보고서(Quarterly/Annual) 추출
            stmt_list.sort(key=lambda x: x['date'], reverse=True)
            latest_stmt = stmt_list[0]
            
            # Tiingo Statements 구조:
            # { 'statementData': { 'incomeStatement': [{'dataCode': 'eps', 'value': ...}, ...], ... } }
            # 이를 딕셔너리 형태 {Key: Value}로 변환하여 접근 용이하게 처리
            if 'statementData' in latest_stmt:
                raw_data = latest_stmt['statementData']
                for section in ['incomeStatement', 'cashFlow', 'overview', 'balanceSheet']:
                    for item in raw_data.get(section, []):
                        stmt_data[item.get('dataCode')] = item.get('value')

        # 3. 데이터 통합
        # Daily 데이터와 Statement 데이터를 결합
        ev = daily_latest.get('enterpriseVal')
        ebitda = stmt_data.get('ebitda')
        
        data = {
            "Symbol": ticker,
            "Date": daily_latest.get('date'),
            
            # --- Valuation Metrics (Daily) ---
            "MarketCap": daily_latest.get('marketCap'),
            "EnterpriseValue": ev,
            "PER": daily_latest.get('peRatio'),
            "PBR": daily_latest.get('pbRatio'),
            "PEG": daily_latest.get('trailingPEG1Y'),
            
            # --- Financial Metrics (Statements) ---
            "EPS": stmt_data.get('epsDiluted'),    # 희석 EPS
            "ROE": stmt_data.get('roe'),
            "ROA": stmt_data.get('roa'),
            "FCF": stmt_data.get('freeCashFlow'),  # 잉여현금흐름
            "EBITDA": ebitda,
            
            # --- Calculated Metrics ---
            "EV/EBITDA": (ev / ebitda) if (ev and ebitda) else None
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
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Gemini 3 Pro 모델 설정
# GOOGLE_API_KEY 환경 변수에서 명시적으로 로드하거나, 직접 문자열로 입력할 수 있습니다.
google_api_key = os.environ.get("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro",
    google_api_key=google_api_key, # 명시적 전달
    temperature=0.1,
    convert_system_message_to_human=True # Google 모델 특성에 따른 옵션 필요시 사용
)

# 번역 및 요약 프롬프트
translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 금융 분석가이자 번역가입니다. 제공된 금융 뉴스를 분석하여 다음 형식에 맞춰 한국어로 작성하세요:\n\n1. **제목**: 한국어로 번역된 제목\n2. **핵심 요약**: 뉴스 내용을 바탕으로 투자자에게 중요한 핵심 내용을 3줄 이내로 요약\n3. **원문 정보**: 원문 제목과 링크(제공된 경우)를 표기"),
    ("user", "뉴스 데이터:\n제목: {title}\n내용: {description}\n링크: {url}")
])

# LCEL(Language Chain Expression Language)로 체인 구성
translate_chain = translate_prompt | llm | StrOutputParser()
```

### 3.1.1 API Key 설정 가이드 (Best Practices)

`ChatGoogleGenerativeAI`를 사용할 때 API Key를 설정하는 방법은 크게 두 가지가 있습니다. 상황에 맞게 선택하여 사용하세요.

**방법 A: 암시적(Implicit) 설정 (간편함)**
라이브러리가 OS의 환경 변수 `GOOGLE_API_KEY`를 자동으로 감지하여 사용합니다. 코드가 간결해지지만, 어떤 키를 사용하는지 명시적으로 보이지 않을 수 있습니다.

```python
# 별도의 전달 없이 초기화하면 os.environ["GOOGLE_API_KEY"]를 자동으로 사용
llm = ChatGoogleGenerativeAI(model="gemini-3-pro")
```

**방법 B: 명시적(Explicit) 설정 (권장)**
`google_api_key` 파라미터를 통해 직접 키를 전달합니다. 여러 개의 API Key를 관리하거나(예: `PROD_KEY`, `DEV_KEY`), 코드의 명확성을 높이고 싶을 때 사용합니다. 본 가이드에서는 이 방식을 채택했습니다.

```python
import os
my_api_key = os.environ.get("MY_CUSTOM_GOOGLE_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro",
    google_api_key=my_api_key # 직접 지정
)
```

### 3.1.2 GitHub Actions (CI/CD) 환경 설정

GitHub Actions와 같은 CI/CD 환경에서 API Key를 안전하게 관리하는 방법입니다.

1.  **GitHub Secrets 등록**:
    *   GitHub 저장소 페이지 이동.
    *   `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret` 클릭.
    *   **Name**: `GOOGLE_API_KEY`
    *   **Value**: 실제 Gemini API 키 값 입력.

2.  **Workflow 파일(.yaml) 설정**:
    *   Step 설정에서 `env` 키워드를 사용하여 Secret 값을 환경 변수로 주입합니다.

```yaml
steps:
  - name: Run Stock Analysis Script
    env:
      GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
    run: python mystock_analyzer.py
```

### 3.1.3 GitHub Actions에서 Keyring 명령어 사용 가이드

만약 코드를 수정하지 않고(`keyring.get_password` 그대로 유지), GitHub Actions 환경에서도 `keyring` 명령어를 통해 API Key를 주입하고 싶다면 다음과 같이 설정합니다.

GitHub Actions(Linux 환경)는 기본적으로 키링 백엔드가 없으므로, **`keyrings.alt`** 패키지를 추가로 설치하여 파일 기반의 백엔드를 사용하도록 해야 합니다.

**Workflow YAML 예시:**

```yaml
steps:
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.9'

  - name: Install Dependencies
    # keyrings.alt 패키지 필수 (Linux Headless 환경 지원용)
    run: pip install keyring keyrings.alt

  - name: Setup Keyring
    # Secrets 값을 가져와 keyring에 저장 (비대화형)
    run: |
      printf "${{ secrets.TIINGO_API_KEY }}" | keyring set tiingo noriskfullpush
      
  - name: Run Script
    # 코드에서는 로컬과 동일하게 keyring.get_password("tiingo", "noriskfullpush") 사용 가능
    run: python mystock_analyzer.py
```

이 방식을 사용하면 파이썬 코드를 로컬/서버 구분 로직 없이(`if/else` 없이) 하나로 유지할 수 있는 장점이 있습니다.

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
            # LangChain을 통한 번역 및 요약 수행
            result_text = translate_chain.invoke({
                "title": article['title'],
                "description": article['description'],
                "url": article['url']
            })
            
            processed_news.append({
                "published_date": article['publishedDate'],
                "original_title": article['title'],
                "analysis_result": result_text, # LLM이 포맷팅한 전체 결과 저장
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
    
    print("\n[Latest News Analysis]")
    for news in result['news']:
        print(f"{news['analysis_result']}\n")
        print("-" * 50)
```

## 5. 요약 및 확장 포인트

1.  **모델 변경**: `ChatGoogleGenerativeAI`를 사용하여 **Gemini 3 Pro** 모델을 지정함으로써, 고성능의 다국어 처리 및 금융 문맥 이해 능력을 활용할 수 있습니다.
2.  **데이터 무결성**: Tiingo API는 금융 데이터에 특화되어 있으므로, 데이터가 없을 경우(`None`)에 대한 예외 처리가 중요합니다.
3.  **확장성**: `StockAnalyzer` 클래스를 확장하여 LangChain Agent Tool로 등록하면, "테슬라 PER 알려주고 뉴스 요약해줘"와 같은 챗봇 형태로 쉽게 발전시킬 수 있습니다.
