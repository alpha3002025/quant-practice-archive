미국 주식의 개별종목 1개에 대해 다음 기능들을 수행하는 데이터 파이프라인을 구현하려고 합니다.

- 주요 뉴스를 한국어로 번역
- tiingo API 를 활용해 해당 주식의 펀더멘털 데이터를 조회
  - (1) 주요 현재가격 대비 비율지표 (PER, EPS, PEG, EV/EBITDA, FCF)
  - (2) 분기 재무 주요 지표 (ROE, ROA)


이 작업을 langchain 을 통해서 데이터 파이프라인을 만들수 있다면 langchaing 설정과정부터 시작해서 전반적인 구현 방안을 설명해주시기 바랍니다.<br/>

AI 모델은 Gemini 3 Pro 를 사용합니다.<br/>

프로그래밍 언어는 python 을 사용합니다.<br/>

tiingo API KEY 는 이미 소유하고 있습니다. 가급적이면 python tiingo library 를 사용하는 방식으로 안내하세요.<br/>
