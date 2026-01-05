# 브리핑봇 환경설정 : Tiingo, Finnhub, Yahooquery 세팅 + 사용법
gemini 가 정리한 건 여기 저기 중요한 내용이 여러 파일로 분산되어 있어서 내 목적과 완전하게 부합되지 않아 docs 에 정리함. 앞으로 `docs` 붙은 문서는 모두 내가 직접 gemini 로 찾은 내용들을 각각 정리하고 종합한 문서로 이름을 붙이기로 결정함
<br/>


## 공식문서
python library document
- https://pypi.org/project/tiingo/
- https://tiingo-python.readthedocs.io/en/latest/
  - https://pypi.org/project/tiingo/ 내의 'Further Docs' 섹션에서 안내

api.tingo.com
- https://app.tiingo.com/
- 공식페이지에서 token 확인시 하단에서 안내하는 Link


<br/>

## 1. 환경 설정 (Setup)
### virtualenv 설치
virtualenv 가 설치되지 않았다면?
```bash
pip install virtualenv
```
<br/>

### virtualenv 활성화
```bash
virtualenv env-py-quant
source env-py-quant/bin/activate
```
<br/>

### python 라이브러리 설치
```bash
pip install langchain langchain-google-genai langchain-anthropic tiingo pandas keyring yahooquery finnhub
```
<br/>

- `langchain`: langchain 생태계
- `langchain-google-genai` : Google의 Gemini 모델을 사용하기 위한 라이브러리 (현재 미사용(Gemini API KEY 불안정으로 인해))
- `langchain-anthropic` : Anthropic의 Claude 모델을 사용하기 위한 라이브러리
- `keyring` : API KEY 관리
- `yahooquery` : 주식 데이터 조회를 위한 크롤링 라이브러리
- `tiingo` : 주식 데이터 조회를 위한 API라이브러리
- `finnhub` : 주식 데이터 조회를 위한 API 라이브러리
<br/>

### keyring
pip 라이브러리를 설치합니다. (참고 : 위에서 설치함)
```python
pip install keyring
```
<br/>

#### tiingo API KEY 설정
```bash
printf "{API Key}" | keyring set tiingo {계정명}
```
<br/>

`keyring` 라이브러리를 설치하면 `keyring` 명령어 도구(CLI)도 같이 설치됩니다.<br/>

`keyring` 라이브러리를 통해 tiingo API KEY를 명령형 프롬프트에서 설정하는 방식은 다음과 같습니다.<br/>
```bash
keyring set tiingo {api_user}
# 명령어를 실행하면 비밀번호 입력 프롬프트가 뜹니다.
# Password for 'api_user' in 'tiingo': 여기에 {트큰 입력} 입력
```
<br/>

파라미터(비대화형)로 전달 해서 설치하는 방식도 있습니다. 스크립트 등에서 사용자 입력 없이 비밀번호를 설정해야 할 경우, 파이프(`|`)를 통해 값을 전달할 수 있습니다.
e.g.
```bash
# printf를 사용하여 줄바꿈 없이 전달
printf "abcdefg12345" | keyring set tiingo {계정명}
```
<br/>

#### finnhub API KEY 설정
이번에는 설명을 생략하고 명령어만 정리해보면 다음과 같습니다.
```bash
## 명령형으로
keyring set finnhub {계정명}

## 또는 파이프를 사용하여 줄바꿈 없이 전달
printf "abcdefg12345" | keyring set finnhub {계정명}
```
<br/>

### yahooquery 설정
```bash
pip install yahooquery
```
<br/>


### 쉘스크립트로 정리
github workflow 를 위해 쉘스크립트로 정리
- Dockerfile 로 할까 생각 중이긴 한데 일단 정리해뒀다.
```bash
### virtualenv (docker 를 쓸 경우 아래 3줄은 필요없긴 함)
pip install virtualenv
virtualenv env-py-quant
source env-py-quant/bin/activate

### python 라이브러리 설치
pip install langchain langchain-anthropic langchain-google-genai google-generativeai langchain-community tiingo finnhub yahooquery pandas keyring keyrings.alt beautifulsoup4 requests
# pip install -U langchain-google-genai
# pip install google-generativeai

### tiingo api key 설정
printf "{토큰값}" | keyring set tiingo {계정명}
```
<br/>


### github actions 에서 keyring 사용
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
    run: pip install langchain langchain-anthropic langchain-google-genai google-generativeai langchain-community tiingo finnhub yahooquery pandas keyring keyrings.alt beautifulsoup4 requests

  - name: Setup Keyring
    # Secrets 값을 가져와 keyring에 저장 (비대화형)
    run: |
      printf "${{ secrets.TIINGO_API_KEY }}" | keyring set tiingo noriskfullpush
      
  - name: Run Script
    # 코드에서는 로컬과 동일하게 keyring.get_password("tiingo", "noriskfullpush") 사용 가능
    run: python mystock_analyzer.py
```

이 방식을 사용하면 파이썬 코드를 로컬/서버 구분 로직 없이(`if/else` 없이) 하나로 유지할 수 있는 장점이 있습니다.

<br/>
<br/>


### gemini API KEY 발급 및 설정

🔑 Gemini API 키 발급 및 확인 방법
- Google AI Studio 접속: 먼저 Google AI Studio(aistudio.google.com) 사이트에 접속합니다.
- 구글 계정 로그인: API를 사용할 구글 계정으로 로그인합니다.
- API 키 메뉴 선택: 화면 왼쪽 사이드바 메뉴에서 'Get API key' (또는 'API 키 받기') 버튼을 클릭합니다.
- 키 생성: * 새로운 프로젝트에서 키를 만들려면 **'Create API key in new project'**를 클릭합니다.
  - 기존에 생성된 구글 클라우드 프로젝트가 있다면 해당 프로젝트를 선택하여 키를 생성할 수도 있습니다.
- 키 복사 및 보관: 생성된 API 키 문자열이 나타나면 'Copy' 버튼을 눌러 복사합니다.

<br/>

### 참고 : Tiingo 뉴스 API 403 Forbidden
무료계정으로 뉴스 API 조회시 Forbidden 에러가 발생한다면 유료구독을 안해서다. 최근 뉴스들이 대부분 유료계정에서만 볼수 있는 자료여서일것으로 보인다. 내 경우에는 4시간을 다른 API를 찾아 돌아다니다가 결국 유료결제 한번에 바로 해결됐다. ✨
자본주의 사회...속에서 취업준비중인 나... 눙물닦자...<br/>
<br/>


### 기사 스크래핑을 위한 부가 라이브러리
```
pip install langchain-community beautifulsoup4
```
<br/>


### Gemini API Key 사용관련
아직 Gemini 를 Langchain 에서 사용하려고 할때 에러가 발생한다. 라이브러리의 호환성이 불안정한 것인지 아니면 Gemini 에서 API 사용하는 기능이 불안정하게 제공되는 것인지 아직은 파악이 안되었다.<br/>
<br/>

그래서 Claude 를 사용하기로 했다. 뭐... 약간 문과적인 작업은 Sonnet 계열이 좋긴해. 글도 잘쓰고.. 그래서 뭐 Gemini 를 사용하지 않은게 아쉽긴 하지만 Sonnet 사용하는 것도 나쁘진 않은 선택같다.<br/>
<br/>

