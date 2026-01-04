workspace/1-langraph-bot-fundamental-vs-price/briefing-bot.py 을 한국시간 오전 7시, 오후 7시에 Github Workflow 를 통해 실행하려합니다.

e.g.
```bash
python workspace/1-langraph-bot-fundamental-vs-price/briefing-bot.py AAPL
```
<br/>


필요한 환경변수명은 다음과 같으며 Github Repository 내의 Secretes and variables / Actions 내에 설정되어 있습니다.
- TIINGO_API_KEY
- CLAUD_API_KEY
- GEMINI_API_KEY
- SLACK_WEBHOOK_URL


필요한 python 의존성들은 다음과 같습니다.
```bash
### virtualenv (docker 를 쓸 경우 아래 3줄은 필요없긴 함)
# pip install virtualenv
# virtualenv env-py-quant
# source env-py-quant/bin/activate

### python 라이브러리 설치
pip install langchain langchain-anthropic langchain-google-genai google-generativeai tiingo pandas keyring


### tiingo api key 설정
printf "{토큰값}" | keyring set tiingo {계정명}
```
<br/>


환경변수들은 각각 keyring 에 저장하려고 하며 예를 들면 다음의 형식으로 저장하려고 합니다.
```yaml
steps:
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.9'

  - name: Install Dependencies
    # keyrings.alt 패키지 필수 (Linux Headless 환경 지원용)
    run: pip install keyring keyrings.alt langchain langchain-anthropic langchain-google-genai google-generativeai tiingo pandas

  - name: Setup Keyring
    # Secrets 값을 가져와 keyring에 저장 (비대화형)
    run: |
      printf "${{ secrets.TIINGO_API_KEY }}" | keyring set tiingo noriskfullpush
      printf "${{ secrets.CLAUD_API_KEY }}" | keyring set claude_quant_automation noriskfullpush
      printf "${{ secrets.GEMINI_API_KEY }}" | keyring set gemini_quant_automation noriskfullpush
      printf "${{ secrets.SLACK_WEBHOOK_URL }}" | keyring set slack_webhook_url noriskfullpush
      
  - name: Run Script
    # 코드에서는 로컬과 동일하게 keyring.get_password("tiingo", "noriskfullpush") 사용 가능
    run: python workspace/1-langraph-bot-fundamental-vs-price/briefing-bot.py AAPL
```
<br/>

브랜치는 main 브랜치에서 수행합니다.
이에 적합한 github workflow 를 ./github/workflows/breifing-bot-aapl.yaml 파일에 작성하세요.
