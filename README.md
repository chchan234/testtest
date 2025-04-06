# Free TC Generator (자동 테스트케이스 생성기)

기획서 문서에서 자동으로 테스트케이스를 생성하는 시스템입니다.

## 기능

- DOCX, PDF 문서에서 텍스트 추출 및 청크 분할
- 텍스트 임베딩을 통한 벡터 DB 구축
- RAG 방식으로 테스트케이스 자동 생성
- 테스트케이스 검증 및 피드백 제공
- 엑셀 형식으로 결과 내보내기

## 설치 방법

### 1. 선행 조건

- Python 3.8 이상
- 패키지 설치를 위한 pip

### 2. 자동 설치 (권장)

```bash
# 저장소 복제
git clone https://github.com/chchan234/free_tc_generator.git
cd free_tc_generator

# 설치 스크립트 실행
python install.py
```

### 3. 수동 설치

```bash
# 저장소 복제
git clone https://github.com/chchan234/free_tc_generator.git
cd free_tc_generator

# 필요한 디렉토리 생성
mkdir -p data/embeddings data/output data/processed data/raw

# PyTorch 설치 (CPU 버전)
pip install torch>=2.2.0 --index-url https://download.pytorch.org/whl/cpu

# 기본 패키지 설치
pip install -r requirements.txt
```

## 실행 방법

```bash
# 애플리케이션 실행
python run_app.py
```

웹 브라우저에서 표시되는 주소(예: http://localhost:8501)로 접속하여 사용할 수 있습니다.

## Streamlit Cloud 배포

이 프로젝트는 Streamlit Community Cloud에 쉽게 배포할 수 있도록 설정되어 있습니다.

### 배포 방법

1. Streamlit Community Cloud에 로그인 (https://streamlit.io/cloud)
2. "New app" 버튼 클릭
3. 다음 설정으로 앱 배포:
   - **Repository**: `chchan234/free_tc_generator` (또는 귀하의 포크)
   - **Branch**: `main`
   - **Main file path**: `ui/app.py`
   - **Python version**: `3.10` (권장)

### 배포 구성 파일

프로젝트에는 Streamlit Cloud 배포에 필요한 다음 구성 파일이 포함되어 있습니다:

- **requirements.txt**: 파이썬 패키지 의존성
- **packages.txt**: 시스템 패키지 의존성 (Rust 컴파일러 등)
- **setup.sh**: 배포 환경 초기화 스크립트
- **.streamlit/config.toml**: Streamlit 설정

## 사용 방법

1. **문서 업로드**: DOCX 또는 PDF 기획서를 업로드합니다.
2. **데이터 처리**: 문서를 텍스트로 추출하고 청크로 분할합니다.
3. **임베딩 생성**: 텍스트 청크를 벡터로 변환합니다.
4. **테스트케이스 생성**: RAG 방식으로 테스트케이스를 생성합니다.
5. **검증 및 피드백**: 생성된 테스트케이스를 검증하고 피드백을 제공받습니다.
6. **엑셀 내보내기**: 최종 결과를 엑셀 파일로 다운로드합니다.

## 문제 해결

설치 과정에서 문제가 발생하면 다음 사항을 확인하세요:

1. Python 버전 확인: Python 3.8 이상이 필요합니다.
2. 가상 환경 사용: 가상 환경(venv 또는 conda)을 사용하여 의존성 충돌을 방지하세요.
3. PyTorch 버전: CPU 버전의 PyTorch를 사용하면 Rust 컴파일러 없이도 설치할 수 있습니다.
4. Tokenizers 오류: `tokenizers` 패키지 빌드에 실패하면 pre-built wheel을 사용하세요.

## 라이센스

MIT License