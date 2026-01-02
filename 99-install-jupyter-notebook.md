가상환경 생성 (권장)
```bash
# 'env-book-practice-py-quant'라는 이름의 Python 3.10 환경 생성 (이름은 자유롭게 변경 가능)
conda create -n env-book-practice-py-quant python=3.10

# 생성한 가상환경 활성화
conda activate env-book-practice-py-quant
```
<br/>

Jupyter Notebook 설치
```bash
# 기본 Jupyter Notebook 설치
conda install jupyter notebook

# (선택 사항) 데이터 분석 필수 패키지 함께 설치 (pandas, numpy, matplotlib 등)
conda install pandas numpy matplotlib seaborn scikit-learn
```

Jupyter Notebook 실행
설치가 완료되면 터미널에서 다음 명령어로 실행합니다.

```bash
jupyter notebook
```

명령어를 실행하면 자동으로 기본 웹 브라우저(Safari, Chrome 등)가 열리면서 Jupyter Notebook 홈 화면(`http://localhost:8888/tree`)이 나타납니다.

deactivate 는 다음과 같이 할수 있습니다.
```bash
# To deactivate an active environment, use
$ conda deactivate
```
<br/>

---

(참고) VS Code 연동
브라우저 대신 VS Code에서 Jupyter Notebook을 사용하고 싶다면:
1.  VS Code를 실행하고 `.ipynb` 파일을 엽니다.
2.  우측 상단의 `커널 선택 (Select Kernel)` 버튼을 클릭합니다.
3.  **Python Environments** > 위에서 생성한 `env-book-practice-py-quant`를 선택합니다.
4.  이제 VS Code 내에서 코드 셀을 실행할 수 있습니다.

<br/>

---
## Troubleshooting

### Error: `zsh: command not found: conda`

터미널에서 `conda` 명령어를 입력했을 때 위와 같은 에러가 발생한다면, Miniforge가 설치되었으나 **환경 변수(Conda Init) 설정이 쉘에 적용되지 않은 상태**입니다.

**해결 방법:**

1.  **Miniforge 설치 경로 확인 및 초기화 실행**
    Miniforge가 기본 경로(`~/miniforge3`)에 설치되었다고 가정하고 다음 명령어를 실행하여 쉘 설정을 초기화합니다.

    ```bash
    # 설치된 conda 바이너리를 직접 호출하여 init 실행
    ~/miniforge3/bin/conda init zsh
    ```

2.  **설정 적용**
    위 명령어를 실행하면 `~/.zshrc` 파일이 수정됩니다. 변경 사항을 현재 터미널에 적용하기 위해 다음 명령어를 입력하거나, 터미널을 껐다가 다시 켭니다.

    ```bash
    source ~/.zshrc
    ```

3.  **확인**
    이제 다시 `conda` 명령어를 입력해 봅니다.
    ```bash
    conda --version
    ```
    정상적으로 버전이 출력되면 해결된 것입니다.

### Error: `PackagesNotFoundError: The following packages are missing from the target environment: - python=3.10`
```bash
$ conda create -n env-book-practice-py-quant python=3.10
Retrieving notices: done
Channels:
 - 
Platform: osx-arm64
Collecting package metadata (repodata.json): done
Solving environment: failed

PackagesNotFoundError: The following packages are missing from the target environment:

  - python=3.10
```


`PackagesNotFoundError`는 Conda가 **현재 설정된 채널(저장소)에서 요청한 패키지(python=3.10)를 찾을 수 없을 때** 발생하는 에러입니다.
특히 로그에 `Channels: -` 처럼 채널 목록이 비어 있거나 `defaults` 채널만 설정되어 있는 경우, 최신 Python 버전을 찾지 못할 수 있습니다. Miniforge는 기본적으로 `conda-forge` 채널을 사용해야 합니다.

**해결 방법:**

1.  **채널 확인하기**
    현재 Conda에 설정된 채널 목록을 확인합니다.
    ```bash
    conda config --show channels
    ```
    이 목록에 `conda-forge`가 없다면 추가해주어야 합니다.

2.  **`conda-forge` 채널 추가 (영구 설정)**
    가장 권장하는 방법은 `conda-forge`를 기본 채널로 설정하는 것입니다.
    ```bash
    conda config --add channels conda-forge
    conda config --set channel_priority strict
    ```

3.  **명령어 실행 시 채널 명시 (일회성 해결)**
    설정을 바꾸지 않고 당장 설치만 하고 싶다면 `-c` (channel) 옵션으로 `conda-forge`를 직접 지정하면 해결됩니다.
    ```bash
    conda create -n env-book-practice-py-quant python=3.10 -c conda-forge
    ```


### 기본으로 설치되는 패키지들

`python=3.10` 환경을 생성할 때, Python 구동에 필요한 최소한의 필수 라이브러리들이 자동으로 함께 설치됩니다. 로그에 나타난 패키지들의 역할은 다음과 같습니다.

*   **`python`**: 요청한 Python 인터프리터 (버전 3.10.19).
*   **`pip`**: Python 패키지 관리자. 가상환경 내에서 `pip install`을 쓰기 위해 필수입니다.
*   **`wheel`, `setuptools`**: Python 패키지를 빌드하고 설치할 때 필요한 기본 도구입니다.
*   **`openssl`**: HTTPS 통신 및 보안 기능을 위한 라이브러리. `pip`나 `requests` 등이 안전하게 인터넷에 연결하려면 필요합니다.
*   **`ca-certificates`**: 보안 인증서 모음.
*   **`readline`, `ncurses`**: 터미널에서 화살표 키, 명령어 히스토리 등을 사용하기 위한 라이브러리.
*   **`tzdata`**: 전 세계 시간대(Timezone) 정보를 담은 데이터베이스.
*   **기타 (`libsqlite`, `libzlib`, `libffi` 등)**: Python 표준 라이브러리가 OS 기능(압축, 데이터베이스, 시스템 호출 등)을 사용하기 위해 의존하는 저수준 C 라이브러리들입니다.

이 패키지들은 Python 환경이 "정상적으로 돌아가기 위한" 최소한의 뼈대(Base)라고 보시면 됩니다.

---

### 참고: Conda 업데이트 경고

```
==> WARNING: A newer version of conda exists. <==
    current version: 25.11.0
    latest version: 25.11.1
```

위와 같은 경고는 현재 설치된 Conda 툴 자체의 버전이 구버전이라는 뜻입니다. 필수적인 것은 아니지만, 버그 수정이나 성능 향상을 위해 다음 명령어로 업데이트해 두는 것이 좋습니다.

```bash
conda update -n base -c conda-forge conda
```


### antigravity 에서 안될때 (Jupyter Kernel 미표시 문제)

터미널에서 `conda activate`로 가상환경을 활성화했음에도 불구하고, Antigravity나 Jupyter Notebook의 커널 선택 목록에 해당 가상환경이 나타나지 않는 경우가 있습니다. 

이는 **해당 가상환경이 Jupyter Kernel로 명시적으로 등록되지 않았기 때문**입니다. 단순히 가상환경을 만드는 것만으로는 Jupyter가 자동으로 인식하지 못합니다.

해결 방법은 다음과 같습니다:

1. **가상환경 경로 및 이름 확인**
   먼저 커널로 등록하려는 가상환경의 정확한 이름과 경로를 확인합니다.
   ```bash
   conda env list
   ```
   명령어 실행 후 `*` 표시가 있는 것이 현재 활성화된 환경입니다.

2. **ipykernel 설치 확인**
   해당 가상환경에 `ipykernel` 패키지가 설치되어 있어야 합니다.
   ```bash
   conda activate [가상환경이름]
   conda install ipykernel
   ```

3. **커널 등록 명령어 실행**
   다음 명령어를 실행하여 현재 가상환경을 Jupyter Kernel로 등록합니다.
   ```bash
   python -m ipykernel install --user --name=[가상환경이름] --display-name "[표시될이름]"
   ```
   
   예시:
   ```bash
   python -m ipykernel install --user --name=env-book-practice-py-quant --display-name "env-book-practice-py-quant"
   ```

명령어 실행 후에는 커널 목록을 새로고침하면 등록된 환경을 선택할 수 있습니다.

#### 왜 이런 과정이 필요한가요? (상세 원인)

1.  **Conda 가상환경과 Jupyter Kernel은 별개입니다.**
    *   **Conda 가상환경**: Python 실행 파일과 라이브러리들이 모여 있는 **폴더**입니다.
    *   **Jupyter Kernel**: Jupyter에게 "어떤 Python을 어떤 옵션으로 실행해야 하는지" 알려주는 **설정 파일(`kernel.json`)**입니다.
    *   Conda로 가상환경을 만들어도, 이를 Jupyter Kernel로 등록(`python -m ipykernel install ...`)하지 않으면 Jupyter는 해당 환경을 알 수 없습니다.

2.  **등록 후에도 안 보인다면? (새로고침 필요)**
    *   Antigravity나 브라우저는 커널 목록을 캐싱(임시 저장)하고 있을 수 있습니다.
    *   등록 절차를 마친 후에는 반드시 **페이지를 새로고침(F5)** 하거나, 커널 선택 메뉴의 **새로고침(Refresh) 버튼**을 눌러야 새로운 환경이 목록에 나타납니다.