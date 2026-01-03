# n8n 주식 정보 자동화: Python Tiingo 라이브러리 활용 방안

사용자의 요구사항(개별 종목, Python Tiingo 라이브러리 사용, n8n 파이프라인)을 충족하기 위해, n8n의 **`Execute Command` 노드**를 사용하여 로컬의 Python 스크립트를 실행하는 방식을 권장합니다.

이 방식은 n8n 내부의 제한적인 환경 대신, 이미 구축된 로컬 Conda 환경(`env-book-practice-py-quant`)의 라이브러리를 그대로 활용할 수 있어 가장 안정적이고 강력합니다.

---

## 1. 전체 파이프라인 구조

```mermaid
graph LR
    A[Schedule/Webhook] --> B[Execute Command\n(Run Python Script)]
    B -->|JSON Output| C[JSON Parse]
    C --> D[OpenAI / LLM Node\n(뉴스 번역 및 요약)]
    D --> E[Merge & Format\n(Markdown Report)]
    E --> F[Email / Slack]
```

1.  **Trigger**: 스케줄(매일 아침) 또는 수동 실행.
2.  **Execute Command**: 로컬 Python 스크립트를 실행하여 Tiingo 데이터를 JSON 형태로 받아옵니다.
    *   *핵심*: 이 단계에서 `tiingo` 파이썬 라이브러리를 사용합니다.
3.  **LLM (번역)**: 받아온 뉴스 텍스트를 OpenAI 노드 등을 통해 한국어로 번역합니다.
4.  **Reporting**: 데이터를 조합하여 리포트를 생성하고 발송합니다.

---

## 2. Python 스크립트 구현 (Data Fetcher)

먼저, n8n이 실행할 Python 스크립트(`fetch_tiingo_data.py`)를 작성해야 합니다. 이 스크립트는 종목 코드를 받아 펀더멘털과 뉴스를 조회하고, 표준 출력(stdout)으로 JSON을 출력합니다.

**스크립트 기능:**
1.  `tiingo` 라이브러리로 펀더멘털(Daily Valuation) 조회
2.  재무제표(Statements) 데이터를 조회하여 ROE, ROA 등 계산
3.  최신 뉴스 조회
4.  결과를 JSON으로 출력

```python
# 파일명: fetch_tiingo_data.py
import sys
import json
from tiingo import TiingoClient
import keyring

def get_stock_data(ticker):
    # 1. 클라이언트 설정 (Keyring 사용 권장)
    api_key = keyring.get_password("tiingo", "api_user")
    if not api_key:
        api_key = "YOUR_API_KEY_HERE" # Fallback
        
    config = {'session': True, 'api_key': api_key}
    client = TiingoClient(config)

    # 2. 펀더멘털 데이터 (Daily Valuation: PER, PEG, etc.)
    # get_fundamentals_daily()는 PER, EPS, MarketCap 등을 제공
    # 주의: tiingo 라이브러리의 메서드명을 확인해야 함 (기본적으로 HTTP endpoint 래핑)
    # 라이브러리 기능이 제한적일 경우 client._request()를 쓸 수도 있음
    
    # 예시: Daily 엔드포인트 활용
    daily_fund = client.get_fundamentals_daily(ticker, startDate='2024-01-01', asDataFrame=False)
    latest_daily = daily_fund[-1] if daily_fund else {}

    # 3. 뉴스 데이터
    news = client.get_news(tickers=[ticker], limit=3)
    
    # 4. 데이터 정리
    result = {
        "ticker": ticker,
        "metrics": {
            "close": latest_daily.get("close"),
            "peRatio": latest_daily.get("peRatio"),
            "eps": latest_daily.get("eps"), # Trailing
            "pegRatio": latest_daily.get("pegRatio"),
            "evEbitda": latest_daily.get("enterpriseValueEbitdaRatio"),
            "marketCap": latest_daily.get("marketCap"),
            # FCF나 ROE/ROA가 daily에 없다면 statements 엔드포인트 필요할 수 있음
            # Tiingo Daily에 roe가 포함되는 경우가 많음
            "roe": latest_daily.get("roe"), 
            "roa": latest_daily.get("roa")
        },
        "news": [
            {"title": n["title"], "description": n["description"], "url": n["url"]} 
            for n in news
        ]
    }
    
    # JSON 출력
    print(json.dumps(result))

if __name__ == "__main__":
    # 커맨드라인 인자로 티커 받기
    target_ticker = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    get_stock_data(target_ticker)
```

---

## 3. n8n 설정 방법

### Step 1: Execute Command Node 설정
n8n이 로컬의 특정 가상환경(conda)을 사용하여 스크립트를 실행하도록 설정합니다.

*   **Node**: Execute Command
*   **Command**:
    ```bash
    /Users/alpha300uk/miniforge3/envs/env-book-practice-py-quant/bin/python /absolute/path/to/fetch_tiingo_data.py AAPL
    ```
    *   **주의**: 단순히 `python`이라고 쓰면 시스템 파이썬이 실행되어 `tiingo` 라이브러리를 못 찾을 수 있습니다. 반드시 `conda env list`로 확인한 **가상환경의 Python 전체 경로**를 입력하세요.
    *   `AAPL` 부분은 n8n의 변수(Example: `{{$json.ticker}}`)로 동적 교체 가능합니다.

### Step 2: JSON Parsing
Execute Command 노드의 출력(stdout)은 문자열(String)입니다. 이를 n8n에서 데이터로 쓰기 위해 변환합니다.

*   **Node**: Code (JavaScript)
    ```javascript
    // Execute Command의 출력을 JSON으로 파싱
    const outputString = items[0].json.stdout;
    const data = JSON.parse(outputString);
    return [{json: data}];
    ```

### Step 3: 뉴스 번역 (AI Node)
파싱된 데이터 중 `news` 배열을 순회하거나, 텍스트로 합쳐서 LLM에 보냅니다.

*   **Node**: OpenAI (Chat Model)
*   **System Prompt**: "다음 뉴스 제목과 요약을 한국어로 번역하고 한 줄로 요약해."
*   **User Message**: `{{ $json.news[0].title }} - {{ $json.news[0].description }}` (루프를 돌거나 전체 텍스트를 전달)

### Step 4: Markdown 리포트 작성 및 전송
*   **Node**: Set / Edit Fields (Template 생성)
    ```markdown
    # 📈 {{ $json.ticker }} 분석
    
    ## 1. 펀더멘털 지표
    - PER: {{ $json.metrics.peRatio }}
    - EPS: {{ $json.metrics.eps }}
    - ROE: {{ $json.metrics.roe }}
    
    ## 2. 주요 뉴스 (KR)
    {{ $json.translated_news }}
    ```
*   **Node**: Gmail / Slack / Email

---

## 4. 요약

1.  **Python Script**: `tiingo` 라이브러리를 사용해 데이터를 수집하고 JSON으로 뱉어내는 "전용 스크립트"를 만듭니다.
2.  **n8n Execution**: n8n의 `Execute Command` 노드에서 **절대 경로**를 사용해 해당 스크립트를 실행합니다.
3.  **Hybrid Approach**: 복잡한 데이터 조회/계산은 Python에 맡기고, 흐름 제어/번역/알림은 n8n이 담당하는 가장 효율적인 구조입니다.
