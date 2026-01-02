# Python Keyring 라이브러리 사용 가이드
Question
```
python 의 keyring 라이브러리가 뭔지, 만약 tiingo 라는 api 의 token 이 'abcdefg12345' 일때 어떤식으로 사용하는지 설치부터 사용법까지 설명을 98-library-keyring.md 에 작성하세요.
```
<br/>


## 1. Keyring 라이브러리란?

`keyring`은 Python 애플리케이션이 운영체제(OS)의 시스템 키링 서비스에 비밀번호나 API 토큰 같은 민감한 정보를 안전하게 저장하고 액세스할 수 있게 해주는 라이브러리입니다.

- **macOS**: Keychain
- **Windows**: Credential Locker
- **Linux**: KWallet 또는 Secret Service API (Gnome Keyring 등)

이를 사용하면 소스 코드나 설정 파일에 민감한 정보(API Key, Password)를 평문(Plain text)으로 저장하지 않아도 되므로 보안성이 크게 향상됩니다.

---

## 2. 설치 방법

터미널에서 `pip`를 사용하여 설치합니다.

```bash
pip install keyring
```

---

## 3. 사용 시나리오

**목표**: `tiingo`이라는 API 서비스의 토큰 `'abcdefg12345'`를 안전하게 저장하고, Python 코드에서 이를 불러와 사용하는 방법을 알아봅니다.

### 3.1 토큰 저장하기 (Set Password)

토큰을 시스템의 키링에 저장합니다. 이 작업은 최초 1회만 수행하면 됩니다. 파이썬 스크립트로 수행하거나 터미널 명령어로 수행할 수 있습니다.

#### 방법 A: Python 코드로 저장

```python
import keyring

# 서비스 명과 사용자 식별자(username) 정의
service_name = "tiingo"
username = "api_user"  # 식별을 위한 사용자 이름 (임의 지정 가능)
token = "abcdefg12345"

# 시스템 키링에 저장
keyring.set_password(service_name, username, token)

print(f"[{service_name}] 토큰이 안전하게 저장되었습니다.")
```

#### 방법 B: 터미널(CLI)로 저장

`keyring` 라이브러리를 설치하면 `keyring` 명령어 도구도 같이 설치됩니다.

```bash
keyring set tiingo api_user
# 명령어를 실행하면 비밀번호 입력 프롬프트가 뜹니다.
# Password for 'api_user' in 'tiingo': 여기에 abcdefg12345 입력
```

---

### 3.2 토큰 불러와서 사용하기 (Get Password)

이제 실제 애플리케이션 코드에서 저장된 토큰을 불러와 사용하는 방법입니다. 코드 내에 토큰이 직접 노출되지 않습니다.

```python
import keyring

service_name = "tiingo"
username = "api_user"

# 키링에서 토큰 조회
api_token = keyring.get_password(service_name, username)

if api_token:
    print("토큰을 성공적으로 불러왔습니다.")
    
    # 실제 API 사용 예시
    # import requests
    # response = requests.get(
    #     "https://api.tiingo.com/data", 
    #     headers={"Authorization": f"Bearer {api_token}"}
    # )
    
    # 확인용 출력 (실제 운영 코드에서는 출력하지 마세요)
    print(f"사용 중인 토큰: {api_token}") 
else:
    print("토큰을 찾을 수 없습니다. 먼저 토큰을 저장해주세요.")
```

---

### 3.3 토큰 삭제하기 (Delete Password)

저장된 토큰이 더 이상 필요 없거나 잘못 저장되었을 때 삭제하는 방법입니다.

```python
import keyring

service_name = "tiingo"
username = "api_user"

try:
    keyring.delete_password(service_name, username)
    print("토큰이 삭제되었습니다.")
except keyring.errors.PasswordDeleteError:
    print("삭제할 토큰이 존재하지 않습니다.")
```

---

## 4. 요약

1.  **설치**: `pip install keyring`
2.  **저장**: `keyring.set_password("tiingo", "my_id", "abcdefg12345")`
3.  **로드**: `key_token = keyring.get_password("tiingo", "my_id")`

이렇게 하면 소스 코드를 깃허브(GitHub) 등에 올릴 때 실수로 API 키가 유출되는 사고를 방지할 수 있습니다.
