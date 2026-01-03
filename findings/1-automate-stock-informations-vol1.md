# n8n 주식 정보 자동화 파이프라인 구축 가이드

요청하신 미국 주식 개별 종목의 **뉴스 번역**과 **펀더멘털 데이터 조회**를 수행하는 n8n 자동화 파이프라인 구현 방안입니다.

n8n은 노드(Node) 기반의 워크플로우 툴이지만, 복잡한 데이터 처리가 필요할 때는 **Python Code Node**를 활용하는 것이 훨씬 효율적입니다.

---

## 1. 전체 파이프라인 구조 (Workflow)

```mermaid
graph LR
    A[Schedule Trigger\n(매일 아침 8시)] --> B[Set Tickers\n(관심 종목 리스트)]
    B --> C[Split In Batches\n(종목별 순회)]
    C --> D1[HTTP Request\n(Tiingo News)]
    C --> D2[HTTP Request\n(Tiingo Fundamentals)]
    D1 --> E[OpenAI Node\n(뉴스 요약 및 번역)]
    D2 --> F[Code Node (Python)\n(재무 지표 계산/추출)]
    E --> G[Merge Data]
    F --> G
    G --> H[Create Markdown Report]
    H --> I[Email / Slack Send]
```

---

## 2. 단계별 상세 구현

### Step 1: Trigger & Target Setup
- **Schedule Node**: 매일 원하는 시간(예: 한국 시간 오전 7시) 설정
- **Set Node**: 분석 대상 티커 리스트 정의 (예: `['AAPL', 'TSLA', 'NVDA']`)

### Step 2: Tiingo API 데이터 수집 (HTTP Request Nodes)

두 개의 **HTTP Request** 노드를 사용하여 각각 뉴스와 펀더멘털 데이터를 가져옵니다.

#### (1) 뉴스 데이터 (News)
- **Method**: GET
- **URL**: `https://api.tiingo.com/tiingo/news`
- **Query Parameters**:
    - `tickers`: `{{ $json.ticker }}` (현재 루프의 티커)
    - `limit`: `3` (최신 뉴스 3개)
    - `token`: `your_tiingo_api_token`

#### (2) 펀더멘털 데이터 (Fundamentals)
Tiingo는 `daily` 엔드포인트에서 대부분의 Valuation 지표를 제공합니다.
- **Method**: GET
- **URL**: `https://api.tiingo.com/tiingo/fundamentals/{{ $json.ticker }}/daily`
- **Query Parameters**:
    - `token`: `your_tiingo_api_token`

### Step 3: 데이터 가공 (Core Logic)

#### (A) 뉴스 번역 및 요약 (AI Node)
OpenAI(ChatGPT) 노드를 사용하여 뉴스 제목과 설명을 요약/번역합니다.
- **System Prompt**: "당신은 금융 전문 번역가입니다. 주어진 미국 주식 뉴스의 핵심 내용을 3줄 이내의 한국어로 요약하세요."
- **User Input**: Step 2에서 가져온 뉴스 JSON 데이터(`title`, `description`).

#### (B) 펀더멘털 데이터 추출 (Python Code Node)
Tiingo의 Raw JSON 응답에서 요청하신 지표(PER, EPS, PEG, EV/EBITDA, FCF, ROE, ROA)를 추출합니다. n8n의 **Code Node (Language: Python)** 를 사용합니다.

```python
# n8n Code Node 내부 Python 스크립트 예시
# 입력 데이터: Tiingo API Response (items[0].json)

items = _input.all()
output_data = []

for item in items:
    ticker_data = item.json # API 응답 데이터
    
    # Tiingo Daily Fundamentals 응답은 리스트 형태이며 최신 데이터가 마지막에 있을 수 있음
    # 데이터 구조에 따라 인덱싱 필요 (보통 최신이 0번이거나 마지막)
    latest_metrics = ticker_data[0] if isinstance(ticker_data, list) and len(ticker_data) > 0 else {}

    # 1. Valuation Metrics Extraction
    # 데이터가 없을 경우를 대비해 .get() 사용
    metrics = {
        "Ticker": latest_metrics.get("ticker", "Unknown"),
        "PER": latest_metrics.get("peRatio", "N/A"),
        "EPS": latest_metrics.get("eps", "N/A"), # Trailing EPS
        "PEG": latest_metrics.get("pegRatio", "N/A"), # 1년 예상 PEG 등이 포함될 수 있음
        "EV_EBITDA": latest_metrics.get("enterpriseValueEbitdaRatio", "N/A"), # 필드명 확인 필요
        # FCF(Free Cash Flow)는 Daily endpoint에 없을 수 있어 Statements endpoint가 필요할 수 있으나, 
        # Daily 요약에 'pcfRatio'(Price to Cash Flow) 등이 있는지 확인.
        # 정확한 FCF 절대값은 Statements API 필요. 여기서는 예시로 marketCap을 가져옵니다.
        "MarketCap": latest_metrics.get("marketCap", "N/A")
    }
    
    # 2. Accounting Ratios (ROE, ROA)
    # Tiingo Daily Endpoint에 roe, roa 필드가 포함되어 있는 경우가 많습니다.
    metrics["ROE"] = latest_metrics.get("roe", "N/A")
    metrics["ROA"] = latest_metrics.get("roa", "N/A")

    output_data.append({"json": metrics})

return output_data
```
> **참고**: Tiingo API의 `daily` 엔드포인트 필드명은 `peRatio`, `pegRatio`, `roe` 등 직관적입니다. FCF의 경우 계산된 비율(Price/FCF)이 아니라 절대값 액수가 필요하다면 `daily` 대신 `statements` 엔드포인트를 추가로 호출하여 `cashFlow` 데이터를 파싱해야 합니다.

### Step 4: 리포트 생성 및 전송

#### Markdown Report 생성
Merge 노드로 (A)와 (B)의 데이터를 합친 후, **Markdown** 형식으로 메일 본문을 구성합니다.

```markdown
## 📊 {{ $json.Ticker }} 일일 분석 리포트

### 1. 주요 펀더멘털
- **주가수익비율 (PER)**: {{ $json.PER }}
- **주당순이익 (EPS)**: {{ $json.EPS }}
- **PEG**: {{ $json.PEG }}
- **EV/EBITDA**: {{ $json.EV_EBITDA }}
- **수익성 (ROE/ROA)**: {{ $json.ROE }}% / {{ $json.ROA }}%

### 2. 주요 뉴스 (AI 요약)
{{ $json.ai_summary_text }}
```

#### Email Send (Gmail / Outlook Node)
- **Recipient**: 본인 이메일
- **Subject**: `[일일주식] {{ $json.Ticker }} 분석 리포트`
- **Body**: 위에서 생성한 Markdown 텍스트 (HTML 변환 옵션 사용 가능)

---

## 3. 요약 및 추천

1.  **n8n 구현 가능성**: **매우 적합**합니다. HTTP Request로 데이터를 모으고, Python Node로 로직을 처리한 뒤, AI Node로 번역하는 흐름이 자연스럽습니다.
2.  **Code Node 활용**: API 응답의 복잡한 JSON 구조에서 특정 필드만 뽑아내거나, 결측치를 처리(N/A 표시 등)하기 위해 **Python Code Node**를 중간에 배치하는 것이 핵심입니다.
3.  **확장성**: 추후 'ROE가 15% 이상인 경우에만 메일 보내기' 같은 조건 분기(If Node)를 추가하여 알림의 질을 높일 수 있습니다.
