# Free TC Generator (자동 테스트케이스 생성기)

기획서 문서에서 QA 관점의 테스트케이스를 자동으로 생성하는 시스템입니다.

## 핵심 기능

- **QA 관점의 테스트케이스 생성**: 단순 기획서 항목이 아닌, 실제로 검증해야 할 UI, 기능, 예외 상황을 포함한 테스트케이스 생성
- **지능적인 조건 분석**: 기획서의 조건문(ENABLE_USE_ITEM = TRUE 등)을 추출하고 QA 테스트 관점으로 변환
- **UI 및 예외 상황 포함**: 버튼 노출, 팝업 표시, 에러 메시지 등 사용자 경험 확인 포인트 자동 생성
- **DOCX, PDF 문서 지원**: 다양한 형식의 기획서 처리 가능
- **테스트케이스 품질 검증**: 생성된 테스트케이스의 정확성, 완전성, 명확성 평가

## 테스트케이스 변환 규칙

프로그램은 기획서의 다음과 같은 패턴을 자동으로 QA 테스트케이스로 변환합니다:

| 기획서 조건 | QA 테스트케이스 |
|------------|----------------|
| ENABLE_USE_ITEM = TRUE | 사용 버튼이 노출되는지 확인 |
| STACK = 1 | 겹치기 불가일 때 수량 표시가 없는지 확인 |
| IS_DELETE = TRUE | 버리기 버튼이 표시되는지 확인 |
| GRADE = LEGEND | 아이템 색상이 주황색으로 표시되는지 확인 |

이 외에도 많은 UI 상호작용 및 예외 상황에 대한 규칙을 포함하고 있습니다.

## 설치 방법

### 1. 선행 조건

- Python 3.8 이상
- 패키지 설치를 위한 pip

### 2. 자동 설치 (권장)

```bash
# 저장소 복제
git clone https://github.com/your-username/free_tc_generator.git
cd free_tc_generator

# 설치 스크립트 실행
python install.py
```

### 3. 수동 설치

```bash
# 저장소 복제
git clone https://github.com/your-username/free_tc_generator.git
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

## 사용 방법

1. **문서 업로드**: DOCX 또는 PDF 기획서를 업로드합니다.
2. **데이터 처리**: 문서를 텍스트로 추출하고 청크로 분할합니다.
3. **임베딩 생성**: 텍스트 청크를 벡터로 변환합니다.
4. **테스트케이스 생성**: 조건 추출 및 QA 관점 변환을 통해 테스트케이스를 생성합니다.
5. **검증 및 피드백**: 생성된 테스트케이스의 품질을 평가합니다.
6. **엑셀 내보내기**: 최종 결과를 엑셀 파일로 다운로드합니다.

## QA 테스트케이스 예시

| 대분류 | 중분류 | 소분류 | 확인내용 | 결과 | 비고 |
|--------|-------|-------|---------|-----|-----|
| 아이템 시스템 | 아이템 사용 | ENABLE_USE_ITEM | 사용 버튼이 노출되는지 확인 | | 조건별 UI 노출 여부 |
| 아이템 시스템 | 인벤토리 표시 | STACK | 겹치기 불가일 때 수량 표시가 없는지 확인 | | 아이콘 개수 표시 여부 |
| 아이템 시스템 | 아이템 삭제 | IS_DELETE | 버리기 버튼이 표시되는지 확인 | | 삭제 권한 확인 |
| 아이템 시스템 | 아이템 등급 | GRADE | 레전드 등급 아이템이 주황색으로 표시되는지 확인 | | 등급별 색상 구분 |

## 확장 및 커스터마이징

- `engine/rag_engine.py`의 `TC_TRANSFORMATION_RULES` 딕셔너리에 새로운 필드 규칙 추가 가능
- `UI_INTERACTION_PATTERNS`와 `EXCEPTION_PATTERNS`에 새로운 패턴 추가 가능
- `extract_conditional_statements` 함수에 추가 정규식 패턴 정의 가능

## 문제 해결

설치 과정에서 문제가 발생하면 다음 사항을 확인하세요:

1. Python 버전 확인: Python 3.8 이상이 필요합니다.
2. 가상 환경 사용: 가상 환경(venv 또는 conda)을 사용하여 의존성 충돌을 방지하세요.
3. PyTorch 버전: CPU 버전의 PyTorch를 사용하면 Rust 컴파일러 없이도 설치할 수 있습니다.
4. Tokenizers 오류: `tokenizers` 패키지 빌드에 실패하면 pre-built wheel을 사용하세요.

## 라이센스

MIT License