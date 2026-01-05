from yahooquery import Ticker
import numpy as np

print("\n" + "="*50 + "\n[Fundamental Data Extraction]\n" + "="*50)

# 1. Ticker 객체 생성
ticker = Ticker('AAPL')

# 2. 필요한 데이터 모듈 가져오기 (각 프로퍼티는 {ticker: data} 형태의 딕셔너리 반환)
# - key_stats: 주요 통계 (PBR, PEG, EPS 등)
# - summary_detail: 요약 정보 (PER 등)
# - financial_data: 재무 데이터 (ROE, ROA, FCF 등)
key_stats = ticker.key_stats['AAPL']
summary_detail = ticker.summary_detail['AAPL']
fin_data = ticker.financial_data['AAPL']

# 3. 데이터 추출 및 출력
# 에러 방지를 위해 .get() 사용 (데이터가 없을 경우 None 반환)

print(f"Symbol: AAPL")

# EPS (주당 순이익)
eps = key_stats.get('trailingEps')
print(f"EPS (Trailing): {eps}")

# PER (주가수익비율)
per = summary_detail.get('trailingPE')
print(f"PER (Trailing): {per}")

# PBR (주가순자산비율)
pbr = key_stats.get('priceToBook')
print(f"PBR: {pbr}")

# ROE (자기자본이익률)
roe = fin_data.get('returnOnEquity')
print(f"ROE: {roe}")

# ROA (총자산이익률)
roa = fin_data.get('returnOnAssets')
print(f"ROA: {roa}")

# PEG (주가수익성장성비율)
peg = key_stats.get('pegRatio')
print(f"PEG: {peg}")

# FCF (잉여현금흐름)
fcf = fin_data.get('freeCashflow')
print(f"FCF: {fcf}")

# EV (기업가치)
ev = key_stats.get('enterpriseValue')
print(f"Enterprise Value (EV): {ev}")

# EV/EBITDA (기업가치/EBITDA)
ev_ebitda = key_stats.get('enterpriseToEbitda')
print(f"EV/EBITDA: {ev_ebitda}")



print("\n" + "="*50 + "\n[Price & Custom PER Calculation]\n" + "="*50)

# 현재 주가 (financial_data의 'currentPrice' 사용)
current_price = fin_data.get('currentPrice')
# 또는 ticker.price 모듈 사용 가능: ticker.price['AAPL']['regularMarketPrice']
print(f"Current Price: {current_price}")


# 직전 4개 분기 EPS 구하기
# all_financial_data(frequency='q') 사용하여 분기 데이터 가져오기
print("Fetching quarterly data for EPS calculation...")
quarterly_data = ticker.all_financial_data(frequency='q')

# 인덱스 리셋 및 필터링하여 필요한 데이터만 추출
quarterly_data.reset_index(inplace=True)
# AAPL 데이터만 필터링 (이미 AAPL로 요청했지만 안전하게)
aapl_q_data = quarterly_data[quarterly_data['symbol'] == 'AAPL'].sort_values('asOfDate', ascending=False)

# 최근 4개 분기 데이터 선택 (Diluted EPS 기준: 'DilutedEPS' 또는 'BasicEPS' 확인 필요. 보통 'DilutedEPS' 사용)
# yahooquery all_financial_data의 컬럼명은 CamleCase가 아니라 보통 그대로 나오는데, 
# 실제 컬럼명을 확인해야 함. 보통 'DilutedEPS' 혹은 'BasicEPS' 가 있음. 
# 여기서는 'DilutedEPS'를 사용한다고 가정하고 없으면 'BasicEPS' 사용.
eps_col = 'DilutedEPS' if 'DilutedEPS' in aapl_q_data.columns else 'BasicEPS'

if eps_col in aapl_q_data.columns:
    last_4_quarters = aapl_q_data.head(4)
    eps_values = last_4_quarters[eps_col].values
    eps_values_str = ' / '.join([str(val) for val in eps_values])
    
    print(f"Last 4 Quarters EPS ({eps_col}): {eps_values_str}")
    
    # sum_eps_prev_4q = 직전 4개 분기 EPS 합계 (Trailing 12M EPS)
    # PER = Price / EPS_TTM (Trailing Twelve Months) 이므로 4분기 합계를 사용하는 것이 일반적입니다.
    
    sum_eps_prev_4q = np.sum(eps_values)
    print(f"Sum EPS (Last 4 Quarters, TTM): {sum_eps_prev_4q:.2f}")

    # prev_sum_eps_vs_price = (직전 4개 분기 EPS 합계 대비 PER) = 현재 주가 / sum_eps_prev_4q
    if sum_eps_prev_4q and sum_eps_prev_4q != 0:
        prev_sum_eps_vs_price = current_price / sum_eps_prev_4q
        print(f"Price / Sum EPS (last 4q, TTM PER): {prev_sum_eps_vs_price:.2f}")
    else:
        print("Cannot calculate PER (Sum EPS is 0 or None)")
else:
    print(f"EPS column '{eps_col}' not found in quarterly data.")



