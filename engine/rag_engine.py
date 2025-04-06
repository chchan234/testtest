"""
RAG 엔진 모듈: 벡터 DB에서 관련 정보를 검색하고 테스트케이스 생성
"""

from typing import List, Dict, Any, Optional
import numpy as np
import re

from embedding.embedder import search_similar

# QA 관점 테스트케이스 변환 규칙
TC_TRANSFORMATION_RULES = {
    # 상태/설정 관련 규칙
    "ENABLE_USE_ITEM": {
        "TRUE": "사용 버튼이 노출되는지 확인",
        "FALSE": "사용 버튼이 비활성화되는지 확인"
    },
    "STACK": {
        "1": "겹치기 불가일 때 수량 표시가 없는지 확인",
        "DEFAULT": "수량이 올바르게 표시되는지 확인"
    },
    "IS_DELETE": {
        "TRUE": "버리기 버튼이 표시되는지 확인",
        "FALSE": "버리기 기능이 제한되는지 확인"
    },
    "GRADE": {
        "NORMAL": "아이템 색상이 회색으로 표시되는지 확인",
        "RARE": "아이템 색상이 파란색으로 표시되는지 확인",
        "EPIC": "아이템 색상이 보라색으로 표시되는지 확인",
        "LEGEND": "아이템 색상이 주황색으로 표시되는지 확인",
        "DEFAULT": "아이템 등급별 색상이 올바르게 표시되는지 확인"
    },
    "USING_TIME": {
        "DEFAULT": "사용 시간이 올바르게 적용되는지 확인",
        "0": "즉시 사용되는지 확인"
    },
    "COOLDOWN": {
        "DEFAULT": "재사용 대기시간이, 설정한 값({value}초)대로 적용되는지 확인",
        "0": "재사용 대기시간 없이 연속 사용 가능한지 확인"
    },
    
    # 제한 및 조건 관련 규칙
    "LEVEL_LIMIT": {
        "DEFAULT": "필요 레벨({value}) 미만 캐릭터가 아이템을 사용할 수 없는지 확인",
        "0": "레벨 제한 없이 모든 레벨에서 사용 가능한지 확인"
    },
    "CLASS_LIMIT": {
        "DEFAULT": "지정된 클래스({value})만 아이템을 사용할 수 있는지 확인",
        "NONE": "모든 클래스에서 아이템을 사용할 수 있는지 확인"
    },
    
    # 효과 및 결과 관련 규칙
    "EFFECT_ID": {
        "DEFAULT": "지정된 이펙트({value})가 발동되는지 확인",
        "NONE": "이펙트 없이 아이템이 소모되는지 확인"
    },
    "REWARD_TYPE": {
        "GOLD": "골드가 올바르게 지급되는지 확인",
        "EXP": "경험치가 올바르게 지급되는지 확인",
        "ITEM": "보상 아이템이 올바르게 지급되는지 확인",
        "DEFAULT": "보상({value})이 올바르게 지급되는지 확인"
    }
}

# UI 및 상호작용 관련 패턴 식별을 위한 추가 규칙
UI_INTERACTION_PATTERNS = {
    "버튼|버튼을|클릭": "버튼이 정상적으로 동작하는지 확인",
    "팝업|모달|다이얼로그": "팝업이 올바르게 표시되는지 확인",
    "슬롯|인벤토리": "인벤토리 UI가 올바르게 표시되는지 확인",
    "장착|착용": "아이템 장착 시 캐릭터에 올바르게 적용되는지 확인",
    "드래그|드롭": "드래그 앤 드롭 기능이 정상 동작하는지 확인",
    "스왑|교체": "아이템 위치 교체가 올바르게 동작하는지 확인",
    "토스트|알림|메시지": "알림 메시지가 올바르게 표시되는지 확인"
}

# 예외 상황 패턴 식별을 위한 규칙
EXCEPTION_PATTERNS = {
    "인벤토리|가득|꽉|full": "인벤토리가 가득 찼을 때 알림이 표시되는지 확인",
    "레벨|부족|미달": "레벨 제한으로 사용 불가 시 적절한 안내가 표시되는지 확인",
    "최대|최소|범위|제한": "최대/최소 사용 가능 수량을 벗어났을 때 제한되는지 확인",
    "오류|에러|예외": "예외 상황 발생 시 오류 메시지가 명확히 표시되는지 확인",
    "네트워크|연결|접속": "네트워크 불안정 시 적절한 오류 처리가 되는지 확인"
}

# 테스트케이스 생성 프롬프트 템플릿
TESTCASE_GENERATION_PROMPT = """
당신은 기획서 내용을 기반으로 테스트케이스를 생성하는 전문가입니다.
아래 기획서 내용을 분석하여 테스트케이스를 작성해주세요.

기획서 내용:
{context}

다음 형식에 맞추어 테스트케이스를 생성해주세요:
대분류: [시스템 영역, 예: 아이템 시스템]
중분류: [주요 기능, 예: 아이템 능력치]
소분류: [세부 기능, 예: 고유 능력치]
확인내용: [구체적인 테스트 내용, 예: 아이템 장착 시 고유 능력치가 캐릭터에 적용되는지 확인]
결과: [테스트 결과]
비고: [추가 참고사항]

테스트케이스:
"""

def extract_conditional_statements(text: str) -> List[Dict[str, Any]]:
    """
    텍스트에서 조건문 패턴을 추출
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        조건 정보 목록 (필드명, 값, 원문)
    """
    # 조건 패턴 정규식
    patterns = [
        # FIELD_NAME = VALUE 패턴 (대문자 필드명, 등호, 값)
        r"([A-Z_]{2,})\s*=\s*([A-Za-z0-9_]+)",
        
        # FIELD_NAME: VALUE 패턴 (대문자 필드명, 콜론, 값)
        r"([A-Z_]{2,})\s*:\s*([A-Za-z0-9_]+)",
        
        # FIELD_NAME이 VALUE 패턴 (대문자 필드명, '이', 값)
        r"([A-Z_]{2,})이\s*([A-Za-z0-9_]+)",
        
        # FIELD_NAME가 VALUE 패턴 (대문자 필드명, '가', 값)
        r"([A-Z_]{2,})가\s*([A-Za-z0-9_]+)",
        
        # FIELD_NAME은 VALUE 패턴 (대문자 필드명, '은', 값)
        r"([A-Z_]{2,})은\s*([A-Za-z0-9_]+)",
        
        # FIELD_NAME는 VALUE 패턴 (대문자 필드명, '는', 값)
        r"([A-Z_]{2,})는\s*([A-Za-z0-9_]+)"
    ]
    
    extracted_conditions = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            field_name = match.group(1)
            value = match.group(2)
            original_text = match.group(0)
            
            # 불리언 값 처리 (TRUE/FALSE)
            if value.upper() in ["TRUE", "FALSE"]:
                value = value.upper()
            
            extracted_conditions.append({
                "field": field_name,
                "value": value,
                "original": original_text
            })
    
    return extracted_conditions

def transform_to_qa_testcase(conditions: List[Dict[str, Any]], context: str) -> Dict[str, str]:
    """
    추출된 조건을 QA 관점의 테스트케이스로 변환
    
    Args:
        conditions: 추출된 조건 목록
        context: 원본 텍스트 컨텍스트
        
    Returns:
        QA 관점의 테스트케이스
    """
    # 기본 테스트케이스 구조 (비어있는 상태)
    testcase = {
        "대분류": "아이템 시스템",  # 기본값, 컨텍스트에 따라 변경 가능
        "중분류": "",
        "소분류": "",
        "확인내용": "",
        "결과": "",
        "비고": ""
    }
    
    # 컨텍스트에서 중분류, 소분류 추정
    if "장착" in context or "착용" in context:
        testcase["중분류"] = "아이템 장착"
    elif "사용" in context:
        testcase["중분류"] = "아이템 사용"
    elif "구매" in context or "상점" in context:
        testcase["중분류"] = "아이템 구매"
    elif "판매" in context:
        testcase["중분류"] = "아이템 판매"
    elif "버리기" in context or "삭제" in context:
        testcase["중분류"] = "아이템 삭제"
    else:
        testcase["중분류"] = "기본 기능"
    
    # 조건에 따른 소분류 및 확인내용 설정
    check_contents = []
    
    for condition in conditions:
        field = condition["field"]
        value = condition["value"]
        
        # 소분류 설정 (첫 번째 조건 기준)
        if not testcase["소분류"] and field in TC_TRANSFORMATION_RULES:
            testcase["소분류"] = field
        
        # 확인내용 생성
        if field in TC_TRANSFORMATION_RULES:
            rule_map = TC_TRANSFORMATION_RULES[field]
            
            if value in rule_map:
                check_content = rule_map[value]
            elif "DEFAULT" in rule_map:
                # DEFAULT 규칙이 있을 경우 값을 포맷팅
                check_content = rule_map["DEFAULT"].replace("{value}", str(value))
            else:
                # 기본 포맷
                check_content = f"{field}가 {value}일 때 동작 확인"
                
            check_contents.append(check_content)
    
    # UI 및 상호작용 패턴 확인
    for pattern, check in UI_INTERACTION_PATTERNS.items():
        if re.search(pattern, context):
            check_contents.append(check)
            break  # 하나만 추가
    
    # 예외 상황 패턴 확인
    for pattern, check in EXCEPTION_PATTERNS.items():
        if re.search(pattern, context):
            check_contents.append(check)
            break  # 하나만 추가
    
    # 확인내용이 추출되지 않았을 경우
    if not check_contents:
        # 기본 확인내용
        testcase["확인내용"] = "기획서 내용대로 동작하는지 확인"
    else:
        # 가장 구체적인 확인내용 선택 (길이가 긴 것)
        testcase["확인내용"] = max(check_contents, key=len)
    
    return testcase

class RAGEngine:
    """RAG 기반 테스트케이스 생성 엔진"""
    
    def __init__(self, vector_db):
        """
        RAG 엔진 초기화
        
        Args:
            vector_db: FAISS 벡터 DB 정보
        """
        self.vector_db = vector_db
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리와 관련된 청크를 검색
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 수
            
        Returns:
            관련 청크 목록
        """
        # FAISS로 유사 검색 수행
        results = search_similar(self.vector_db, query, top_k=n_results)
        return results
    
    def generate_testcase(self, query: str, context: str) -> Dict[str, str]:
        """
        컨텍스트를 기반으로 테스트케이스 생성
        
        Args:
            query: 사용자 쿼리
            context: 검색된 관련 컨텍스트
            
        Returns:
            생성된 테스트케이스
        """
        # 텍스트에서 조건문 추출
        conditions = extract_conditional_statements(context)
        
        # 조건이 없는 경우 기본 테스트케이스 반환
        if not conditions:
            return {
                "대분류": "아이템 시스템",
                "중분류": "기본 기능",
                "소분류": "일반",
                "확인내용": "기획서 내용대로 동작하는지 확인",
                "결과": "",
                "비고": "조건 없음"
            }
        
        # QA 관점의 테스트케이스로 변환
        testcase = transform_to_qa_testcase(conditions, context)
        
        return testcase

def process_rag(vector_db, user_query: str, n_results: int = 5) -> List[Dict[str, str]]:
    """
    RAG 프로세스 실행 함수
    
    Args:
        vector_db: FAISS 벡터 DB 정보
        user_query: 사용자 쿼리
        n_results: 검색 결과 수
        
    Returns:
        생성된 테스트케이스 목록
    """
    rag_engine = RAGEngine(vector_db)
    
    # 관련 청크 검색
    relevant_chunks = rag_engine.retrieve_relevant_chunks(user_query, n_results=n_results)
    
    # 컨텍스트 통합
    context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
    
    # 테스트케이스 생성
    testcase = rag_engine.generate_testcase(user_query, context)
    
    return [testcase]

def generate_testcases(vector_db, document_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    전체 문서를 기반으로 테스트케이스 생성
    
    Args:
        vector_db: FAISS 벡터 DB 정보
        document_chunks: 문서 청크 목록
        
    Returns:
        생성된 테스트케이스 목록
    """
    rag_engine = RAGEngine(vector_db)
    testcases = []
    
    # 모든 청크 처리
    for chunk in document_chunks:
        # 각 청크를 컨텍스트로 사용
        context = chunk['text']
        
        # 조건문 추출
        conditions = extract_conditional_statements(context)
        
        # 조건이 있는 경우만 테스트케이스 생성
        if conditions:
            testcase = transform_to_qa_testcase(conditions, context)
            testcases.append(testcase)
    
    return testcases