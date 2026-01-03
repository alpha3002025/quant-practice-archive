# Tiingo 라이브러리 설치 및 사용 가이드

## 1. Tiingo란?

**Tiingo**는 고품질의 주식, ETF, 암호화폐, 뉴스 등 다양한 금융 데이터를 제공하는 플랫폼입니다. `tiingo` 파이썬 라이브러리는 Tiingo API를 파이썬 환경에서 쉽고 간편하게 사용할 수 있도록 도와주는 공식 클라이언트 도구입니다.

데이터 분석을 위한 Pandas DataFrame 통합 기능이 뛰어나 퀀트(Quant) 분석에 자주 활용됩니다.

---

## 2. 설치 방법

터미널에서 `pip`를 사용하여 설치합니다. 데이터 처리를 위해 `pandas` 라이브러리도 함께 설치하는 것을 권장합니다.

```bash
pip install tiingo pandas
```

---

## 3. 사전 준비: API Key 설정

Tiingo API를 사용하려면 [Tiingo 웹사이트](https://www.tiingo.com/)에 가입하여 **API Key**를 발급받아야 합니다.

**보안 권장사항:**  
API Key는 코드에 직접 붙여넣기(Hardcoding) 하는 것보다, `keyring` 라이브러리나 환경 변수를 통해 관리하는 것이 안전합니다. 아래 예제에서는 앞서 다룬 `keyring`을 사용하는 방식을 기준으로 설명합니다.

*(Keyring 사용법은 `98-library-keyring.md` 파일을 참고하세요)*

---

## 4. 사용 예제

### 4.1 기본 설정 및 클라이언트 초기화

```python
from tiingo import TiingoClient
import keyring

# 1. API Key 불러오기 (안전한 방식)
# keyring에 'tiingo' 서비스의 'api_user' 계정에 키를 저장해두었다고 가정합니다.
api_key = keyring.get_password("tiingo", "api_user")

if not api_key:
    # 키가 없다면 직접 입력하거나 에러 처리
    print("Keyring에 저장된 키가 없습니다.")
    api_key = "MY_SECRET_API_KEY" # 테스트용 직접 입력

# 2. 설정 딕셔너리 생성
config = {
    'session': True, # HTTP 세션을 유지하여 성능 향상
    'api_key': api_key
}

# 3. 클라이언트 객체 생성
client = TiingoClient(config)
```

### 4.2 주가 데이터 가져오기 (Pandas DataFrame)

Tiingo 라이브러리의 가장 강력한 기능은 데이터를 바로 Pandas DataFrame으로 받아오는 것입니다.

```python
import pandas as pd

# Apple(AAPL)의 2023년 데이터 조회
# frequency: daily(일간), weekly(주간), monthly(월간) 등 설정 가능
df = client.get_dataframe('AAPL',
                          frequency='daily',
                          startDate='2023-01-01',
                          endDate='2023-12-31')

# 결과 출력
print(f"조회된 데이터 수: {len(df)}일")
print(df.head())
print(df.tail())
```

### 4.3 여러 종목 데이터 한번에 가져오기

여러 종목(Ticker)을 리스트로 전달하면, Multi-Index 형태의 DataFrame을 반환받을 수 있습니다.

```python
tickers = ['AAPL', 'GOOGL', 'TSLA']

df_multi = client.get_dataframe(tickers,
                                frequency='daily',
                                startDate='2024-01-01')

# 예: 구글(GOOGL) 데이터만 보기
print(df_multi.loc['GOOGL'].head())
```

---

## 5. 요약

1.  **설치**: `pip install tiingo`
2.  **설정**: `keyring` 등을 이용해 API Key를 안전하게 로드하고 `config` 딕셔너리 구성
3.  **실행**: `TiingoClient(config)` 초기화 후 `client.get_dataframe()` 메서드로 데이터 확보

이 과정을 통해 복잡한 API 호출 코드 없이도 금융 데이터를 손쉽게 분석 환경으로 가져올 수 있습니다.
