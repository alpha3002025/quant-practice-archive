# Tiingo, Finnhub 세팅 + 사용법
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
pip install langchain langchain-google-genai tiingo pandas keyring
```
<br/>

- `langchain`: langchain 생태계
- `langchain-google-genai` : Google의 Gemini 모델을 사용하기 위한 라이브러리 
- `tiingo` : 주식 데이터 조회를 위한 라이브러리
- `keyring` : API KEY 관리

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



### 쉘스크립트로 정리
github workflow 를 위해 쉘스크립트로 정리
- Dockerfile 로 할까 생각 중이긴 한데 일단 정리해뒀다.
```bash
### virtualenv (docker 를 쓸 경우 아래 3줄은 필요없긴 함)
pip install virtualenv
virtualenv env-py-quant
source env-py-quant/bin/activate

### python 라이브러리 설치
pip install langchain langchain-google-genai tiingo pandas keyring

### tiingo api key 설정
printf "{토큰값}" | keyring set tiingo {계정명}
```


