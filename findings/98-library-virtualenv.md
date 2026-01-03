# Virtualenv 사용법 가이드

Python 가상 환경(Virtual Environment)을 관리하기 위한 `virtualenv`의 설치, 활성화, 비활성화 및 전반적인 사용법을 정리합니다.

## 1. Virtualenv란?

프로젝트별로 독립된 Python 실행 환경을 만들어주는 도구입니다. 이를 통해 각 프로젝트마다 서로 다른 버전의 패키지를 충돌 없이 관리할 수 있습니다.

*참고: Python 3.3부터는 표준 라이브러리에 `venv` 모듈이 포함되어 있어, 별도 설치 없이 `python -m venv <이름>` 명령으로도 유사한 기능을 사용할 수 있습니다. 하지만 `virtualenv`는 더 많은 기능과 속도 최적화를 제공합니다.*

## 2. 설치 (Installation)

`virtualenv`는 파이썬 패키지이므로 `pip`를 통해 전역(Global)으로 설치합니다.

```bash
pip install virtualenv
```

설치가 잘 되었는지 확인하려면 버전을 조회해 봅니다.

```bash
virtualenv --version
```

## 3. 가상 환경 생성 (Creation)

프로젝트 폴더로 이동한 후, 원하는 이름(보통 `venv` 또는 `.venv`를 많이 사용)으로 가상 환경을 생성합니다.

```bash
# 기본 사용법
virtualenv venv
```

특정 파이썬 버전을 지정하여 생성하고 싶다면 `-p` 옵션을 사용합니다 (해당 파이썬 버전이 시스템에 설치되어 있어야 함).

```bash
virtualenv -p python3.11 venv
```

## 4. 가상 환경 활성화 (Activation)

가상 환경을 생성한 후에는 이를 **활성화**해야 해당 환경 내에서 패키지를 설치하거나 스크립트를 실행할 수 있습니다. 운영체제에 따라 명령어가 다릅니다.

### macOS / Linux

```bash
source venv/bin/activate
```

활성화되면 터미널 프롬프트 앞에 `(venv)`와 같이 가상 환경 이름이 표시됩니다.

### Windows (cmd)

```cmd
venv\Scripts\activate
```

### Windows (PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```
*권한 오류 발생 시 `Set-ExecutionPolicy Unrestricted` 등의 설정이 필요할 수 있습니다.*

## 5. 가상 환경 사용 (General Usage)

가상 환경이 활성화된 상태(`(venv)` 표시 확인)에서 `pip` 명령어를 사용하면, 해당 가상 환경 폴더 내부에만 패키지가 설치됩니다.

### 패키지 설치

```bash
pip install requests pandas
```

### 설치된 패키지 확인

```bash
pip list
```

### 의존성 파일 생성 및 설치 (requirements.txt)

협업이나 배포를 위해 현재 환경의 패키지 목록을 저장하고 복원하는 방법입니다.

**저장하기 (Freeze):**
```bash
pip freeze > requirements.txt
```

**설치하기 (Install):**
다른 사람이 프로젝트를 받았을 때, 가상 환경을 만들고 활성화한 뒤 다음 명령어로 동일한 환경을 구성할 수 있습니다.
```bash
pip install -r requirements.txt
```

## 6. 가상 환경 비활성화 (Deactivation)

작업을 마치고 원래의 시스템 파이썬 환경으로 돌아가려면 다음 명령어를 입력합니다. (어느 운영체제에서든 동일합니다)

```bash
deactivate
```

## 7. 가상 환경 삭제

가상 환경은 단순히 생성된 **폴더**입니다. 삭제하고 싶다면 해당 폴더(`venv` 등)를 그냥 삭제(휴지통으로 이동 또는 `rm -rf venv`)하면 됩니다. 별도의 삭제 명령어가 존재하지 않습니다.

```bash
rm -rf venv
```

---

**요약 프로세스:**
1.  `virtualenv venv` (생성 - 최초 1회)
2.  `source venv/bin/activate` (활성화 - 작업 시작 시 매번)
3.  `pip install ...` (패키지 관리)
4.  `deactivate` (비활성화 - 작업 종료 시)
