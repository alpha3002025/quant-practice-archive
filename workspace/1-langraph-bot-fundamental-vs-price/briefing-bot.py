import keyring
import pandas as pd
import numpy as np
import requests
import json
import sys

## (1) 번 기능에서 사용 (Tiingo)
from tiingo import TiingoClient
from yahooquery import Ticker

## (2) 번 기능에서 사용 (뉴스 본문 스크래핑)
from langchain_community.document_loaders import WebBaseLoader

## (3) 번 기능에서 사용 (Langchain, Claude)
import time
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


start_date_str = (pd.Timestamp.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
fundamental_start_date = f"{pd.Timestamp.now().year - 1}-01-01"


# Get ticker from command line argument if provided, otherwise default to "AAPL"
if len(sys.argv) > 1:
    search_ticker = sys.argv[1]
    if len(sys.argv) > 2:
        webhook_url = sys.argv[2]
    else:
        webhook_url = keyring.get_password("slack_webhook_url", "noriskfullpush")
else:
    search_ticker = "AAPL"
    webhook_url = keyring.get_password("slack_webhook_url", "noriskfullpush")
    print(f"No ticker argument provided. Defaulting to {search_ticker}. Usage: python briefing-bot.py [TICKER]")


api_key_gemini = keyring.get_password("gemini_quant_automation", "noriskfullpush")
api_key_claude = keyring.get_password("claude_quant_automation", "noriskfullpush")
api_key_tiingo = keyring.get_password("tiingo", "noriskfullpush")


tiingo_config = {}
tiingo_config['session'] = True
tiingo_config['api_key'] = api_key_tiingo
client = TiingoClient(tiingo_config)

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


def get_stock_fundamentals_tiingo(ticker: str):
    print(f"Fetching data for {ticker}...")
    try:
        # 1. Daily Data
        daily_list = client.get_fundamentals_daily(ticker, startDate=fundamental_start_date)
        if not daily_list:
             print("No daily data")
             return None
        
        daily_df = pd.DataFrame(daily_list)
        daily_df['date'] = pd.to_datetime(daily_df['date'])
        daily_latest = daily_df.sort_values('date').iloc[-1]
        
        # 2. Statements Data
        stmt_list = client.get_fundamentals_statements(ticker, startDate=fundamental_start_date)
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


def get_stock_fundamentals_yahooquery(ticker_str: str):
    print(f"Fetching data for {ticker_str}...")

    try:
        # 1. Ticker 객체 생성
        ticker = Ticker(ticker_str)

        # 2. 필요한 데이터 모듈 가져오기 (각 프로퍼티는 {ticker: data} 형태의 딕셔너리 반환)
        # - key_stats: 주요 통계 (PBR, PEG, EPS 등)
        # - summary_detail: 요약 정보 (PER 등)
        # - financial_data: 재무 데이터 (ROE, ROA, FCF 등)
        key_stats = ticker.key_stats[ticker_str]
        summary_detail = ticker.summary_detail[ticker_str]
        fin_data = ticker.financial_data[ticker_str]
        
        # 3. 데이터 추출
        market_cap = summary_detail.get('marketCap')
        # print(f"Market Cap: {market_cap}")

        # EPS (주당 순이익)
        eps = key_stats.get('trailingEps')
        # print(f"EPS (Trailing): {eps}")

        # PER (주가수익비율)
        per = summary_detail.get('trailingPE')
        # print(f"PER (Trailing): {per}")

        # PBR (주가순자산비율)
        pbr = key_stats.get('priceToBook')
        # print(f"PBR: {pbr}")

        # ROE (자기자본이익률)
        roe = fin_data.get('returnOnEquity')
        # print(f"ROE: {roe}")

        # ROA (총자산이익률)
        roa = fin_data.get('returnOnAssets')
        # print(f"ROA: {roa}")

        # PEG (주가수익성장성비율)
        peg = key_stats.get('pegRatio')
        # print(f"PEG: {peg}")

        # FCF (잉여현금흐름)
        fcf = fin_data.get('freeCashflow')
        # print(f"FCF: {fcf}")

        # EV (기업가치)
        ev = key_stats.get('enterpriseValue')
        # print(f"Enterprise Value (EV): {ev}")

        # EBITDA (영업이익)
        ebitda = fin_data.get('ebitda')
        # print(f"EBITDA: {ebitda}")

        # EV/EBITDA (기업가치/EBITDA)
        ev_ebitda = key_stats.get('enterpriseToEbitda')
        # print(f"EV/EBITDA: {ev_ebitda}")

        # 현재 주가 (financial_data의 'currentPrice' 사용)
        current_price = fin_data.get('currentPrice')

        # 직전 4개 분기 EPS
        quarterly_data = ticker.all_financial_data(frequency='q')
        
        prev_4q_eps_values_str = "N/A"
        sum_eps_prev_4q = None
        prev_sum_eps_vs_price = None

        if not quarterly_data.empty:
            quarterly_data.reset_index(inplace=True)
            # 해당 심볼 데이터 필터링
            q_data = quarterly_data[quarterly_data['symbol'] == ticker_str].sort_values('asOfDate', ascending=False)
            
            # EPS 컬럼 확인
            eps_col = 'DilutedEPS' if 'DilutedEPS' in q_data.columns else 'BasicEPS'
            
            if eps_col in q_data.columns:
                last_4_quarters = q_data.head(4)
                eps_values = last_4_quarters[eps_col].values
                # 직전 4개 분기 EPS 문자열
                prev_4q_eps_values_str = ' / '.join([str(val) for val in eps_values])
                
                # 직전 4개 분기 EPS 총합 (TTM EPS)
                sum_eps_prev_4q = np.sum(eps_values)
                
                # prev_sum_eps_vs_price (Price / TTM EPS)
                if sum_eps_prev_4q and sum_eps_prev_4q != 0 and current_price:
                    prev_sum_eps_vs_price = current_price / sum_eps_prev_4q



        data = {
            "Symbol": ticker_str,
            "Date": pd.Timestamp.now().strftime('%Y-%m-%d'), # Yahooquery는 현재 기준 데이터
            "MarketCap": market_cap,
            "PER": per,
            "PBR": pbr,
            "PEG": peg,
            "EPS": eps,
            "ROE": roe,
            "ROA": roa,
            "FCF": fcf,
            "EnterpriseValue": ev,
            "EBITDA": ebitda, 
            "EV/EBITDA": ev_ebitda,
            "PrevEPSValues": prev_4q_eps_values_str,
            "PrevSumEPS": sum_eps_prev_4q,
            "PrevSumEPSvsPrice": prev_sum_eps_vs_price
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
            "startDate": start_date_str
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


def merge_article_content(news_data):
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
    return news_data


def initialize_llm():
    ### Claude (Anthropic) 모델 설정
    print(f"Initializing Claude model: claude-sonnet-4-20250514...")
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key_claude,
        temperature=0.1
    )

    return llm


def generate_chain(prompt_template_str: str):
    # 체인 생성
    prompt = ChatPromptTemplate.from_template(prompt_template_str)
    chain = prompt | llm | StrOutputParser()

    return chain


def analyze_news_data(news_data):
    result = []
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
            
            analyzed = chain.invoke(input_data)
            # print("\n" + analyzed)
            result.append(analyzed)
            
            # Claude는 Rate Limit이 넉넉하므로 별도 딜레이 불필요 (필요시 추가)
            # time.sleep(1)
            
        except Exception as e:
            print(f"Error processing article: {e}")
        
    return result


def send_briefing_slack(ticker, fundamental_data, news_data):
    if not webhook_url:
        print("\n[Slack Error] Webhook URL이 설정되지 않았습니다.")
        return

    # Slack 메시지 구성 (Block Kit)
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 {ticker} 주식 브리핑 ({pd.Timestamp.now().strftime('%Y-%m-%d')})",
                "emoji": True
            }
        },
        {"type": "divider"}
    ]

    # 1. 펀더멘탈 데이터
    fund_text = "*1. 펀더멘탈 데이터 (Tiingo)*\n"
    if fundamental_data:
        for key, value in fundamental_data.items():
            fund_text += f"• *{key}*: {value}\n"
    else:
        fund_text += "데이터를 가져오지 못했습니다.\n"
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": fund_text
        }
    })
    blocks.append({"type": "divider"})

    # 2. 뉴스 데이터
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*2. AI 뉴스 분석 (Claude)*"
        }
    })

    if news_data:
        for news in news_data:
            # 뉴스 텍스트 정리 (줄바꿈 등)
            # 뉴스 포맷이 "기사. 제목 \n - 원문... \n [요약] ..." 형태임
            # 간단하게 포맷팅
            lines = news.split('\n')
            title = lines[0].replace("기사. ", "") if len(lines) > 0 else "No Title"
            
            # URL 추출 시도
            url = ""
            for line in lines:
                if "URL :" in line:
                    url = line.split("URL :")[1].strip()
                    break
            
            # 요약 내용 추출 (간단히 전체 텍스트 사용하되, 너무 길면 Slack 제한 걸릴 수 있음)
            # 여기서는 전체 텍스트를 그대로 넣되, 인용구 처리
            content = news.replace("\n", "\n>")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📰 *{title}*\n{content}"
                }
            })
            blocks.append({"type": "divider"})
    else:
         blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "분석된 뉴스가 없습니다."
            }
        })

    try:
        response = requests.post(
            webhook_url,
            json={"blocks": blocks}
        )
        if response.status_code == 200:
            print(f"\n[Success] Slack으로 메시지를 전송했습니다.")
        else:
            print(f"\n[Error] Slack 전송 실패: {response.status_code} {response.text}")
    except Exception as e:
        print(f"\n[Error] Slack 전송 중 예외 발생: {e}")


### (1) 펀더멘탈 조회 (주석 처리됨)
# fundamental_data = get_stock_fundamentals_tiingo(search_ticker)
fundamental_data = get_stock_fundamentals_yahooquery(search_ticker)
print(json.dumps(fundamental_data, indent=2, default=str))


### (2) 뉴스 조회
print(f"Fetching news for {search_ticker} from Tiingo...")
##### news api 
news_data = get_tiingo_stock_news_with_api(search_ticker, api_key=api_key_tiingo, limit=5)
# print(json.dumps(news_data, indent=2, default=str))


##### 기사 본문 스크래핑 + 병합
print("\n" + "="*50 + "\n[News Data Merging]\n" + "="*50)
print("Fetching full article contents...")
news_data = merge_article_content(news_data)
# print(json.dumps(news_data, indent=2, default=str))


### (3) Claude 뉴스 분석 프롬프트 (Raw Text)
print("\n" + "="*50 + "\n[Claude News Briefing]\n" + "="*50)
##### llm 모델 초기화작업
llm = initialize_llm()
##### 체인 생성
chain = generate_chain(prompt_template_str)

##### 뉴스별 분석 수행
print(f"Analyzing {len(news_data)} articles...")
analyzed_news_data = analyze_news_data(news_data)
print(json.dumps(analyzed_news_data, indent=2, default=str, ensure_ascii=False))

##### Slack 전송 실행
print(f"\nSending Slack message...")
send_briefing_slack(search_ticker, fundamental_data, analyzed_news_data)
