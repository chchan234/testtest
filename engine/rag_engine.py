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
    },
    
    # 스킬 시스템 관련 규칙 추가
    "SKILL_TYPE": {
        "ACTIVE": "액티브 스킬이 올바르게 발동되는지 확인",
        "PASSIVE": "패시브 스킬 효과가 항상 적용되는지 확인",
        "TOGGLE": "토글 스킬 온/오프 전환이 정상 작동하는지 확인",
        "BUFF": "버프 효과가 대상에게 올바르게 적용되는지 확인",
        "DEBUFF": "디버프 효과가 대상에게 올바르게 적용되는지 확인",
        "DEFAULT": "스킬 타입({value})이 설정대로 작동하는지 확인"
    },
    "SKILL_LEVEL": {
        "DEFAULT": "스킬 레벨({value})에 따라 성능이 올바르게 적용되는지 확인",
        "1": "스킬 기본 레벨 효과가 올바르게 적용되는지 확인",
        "MAX": "스킬 최대 레벨 효과가 올바르게 적용되는지 확인"
    },
    "SKILL_TARGET": {
        "SELF": "자기 자신에게 스킬 효과가 적용되는지 확인",
        "SINGLE": "단일 대상에게 스킬 효과가 적용되는지 확인",
        "AOE": "범위 내 모든 대상에게 스킬 효과가 적용되는지 확인",
        "ALL_ALLIES": "모든 아군에게 스킬 효과가 적용되는지 확인",
        "ALL_ENEMIES": "모든 적에게 스킬 효과가 적용되는지 확인",
        "DEFAULT": "지정된 타겟({value})에게 스킬 효과가 적용되는지 확인"
    },
    "SKILL_COST": {
        "DEFAULT": "스킬 사용 시 지정된 코스트({value})가 소모되는지 확인",
        "0": "코스트 없이 스킬을 사용할 수 있는지 확인"
    },
    "EQUIPMENT_SLOT": {
        "WEAPON": "무기 슬롯에 장착 시 효과가 올바르게 적용되는지 확인",
        "ARMOR": "방어구 슬롯에 장착 시 효과가 올바르게 적용되는지 확인",
        "ACCESSORY": "액세서리 슬롯에 장착 시 효과가 올바르게 적용되는지 확인",
        "HEAD": "머리 슬롯에 장착 시 효과가 올바르게 적용되는지 확인",
        "BODY": "몸통 슬롯에 장착 시 효과가 올바르게 적용되는지 확인",
        "HAND": "손 슬롯에 장착 시 효과가 올바르게 적용되는지 확인",
        "FOOT": "발 슬롯에 장착 시 효과가 올바르게 적용되는지 확인",
        "DEFAULT": "지정된 슬롯({value})에 장착 시 효과가 올바르게 적용되는지 확인"
    },
    "EQUIPMENT_SET": {
        "DEFAULT": "세트({value}) 아이템 장착 시 세트 효과가 올바르게 적용되는지 확인",
        "NONE": "세트 효과 없이 장비 효과만 적용되는지 확인"
    },
    "ITEM_REQUIREMENT": {
        "DEFAULT": "아이템 사용 조건({value})을 충족했을 때만 사용 가능한지 확인",
        "NONE": "사용 조건 없이 항상 사용 가능한지 확인"
    },
    "EQUIPMENT_STAT": {
        "ATK": "아이템 장착 시 공격력 스탯이 올바르게 증가하는지 확인",
        "DEF": "아이템 장착 시 방어력 스탯이 올바르게 증가하는지 확인",
        "HP": "아이템 장착 시 체력 스탯이 올바르게 증가하는지 확인",
        "MP": "아이템 장착 시 마나 스탯이 올바르게 증가하는지 확인",
        "CRIT": "아이템 장착 시 치명타 스탯이 올바르게 증가하는지 확인",
        "SPEED": "아이템 장착 시 속도 스탯이 올바르게 증가하는지 확인",
        "DEFAULT": "아이템 장착 시 해당 스탯({value})이 올바르게 증가하는지 확인"
    },
    "SKILL_UNLOCK": {
        "DEFAULT": "필요 레벨({value}) 달성 시 스킬이 자동으로 해금되는지 확인",
        "QUEST": "관련 퀘스트 완료 시 스킬이 해금되는지 확인",
        "ITEM": "특정 아이템 사용 시 스킬이 해금되는지 확인"
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
    "토스트|알림|메시지": "알림 메시지가 올바르게 표시되는지 확인",
    "스킬트리|스킬창": "스킬 UI가 올바르게 표시되는지 확인",
    "아이콘|이미지": "스킬/아이템 아이콘이 올바르게 표시되는지 확인",
    "레벨업|강화": "레벨업/강화 효과가 시각적으로 표시되는지 확인",
    "쿨타임|게이지": "쿨타임/게이지가 올바르게 표시되는지 확인",
    "획득|보상": "아이템/스킬 획득 시 알림이 표시되는지 확인"
}

# 예외 상황 패턴 식별을 위한 규칙
EXCEPTION_PATTERNS = {
    "인벤토리|가득|꽉|full": "인벤토리가 가득 찼을 때 알림이 표시되는지 확인",
    "레벨|부족|미달": "레벨 제한으로 사용 불가 시 적절한 안내가 표시되는지 확인",
    "최대|최소|범위|제한": "최대/최소 사용 가능 수량을 벗어났을 때 제한되는지 확인",
    "오류|에러|예외": "예외 상황 발생 시 오류 메시지가 명확히 표시되는지 확인",
    "네트워크|연결|접속": "네트워크 불안정 시 적절한 오류 처리가 되는지 확인",
    "스킬포인트|부족": "스킬 포인트 부족 시 적절한 안내가 표시되는지 확인",
    "착용불가|장착불가|클래스": "클래스 제한으로 착용 불가 시 안내가 표시되는지 확인",
    "해금|잠금": "스킬이 잠겨있을 때 해금 조건이 표시되는지 확인",
    "소모품|부족": "필요 소모품 부족 시 알림이 표시되는지 확인",
    "중복|이미장착": "이미 장착된 아이템 재장착 시 처리가 올바른지 확인"
}

# 테스트케이스 생성 프롬프트 템플릿
TESTCASE_GENERATION_PROMPT = """
당신은 기획서 내용을 기반으로 테스트케이스를 생성하는 전문가입니다.
아래 기획서 내용을 분석하여 테스트케이스를 작성해주세요.

기획서 내용:
{context}

다음 형식에 맞추어 테스트케이스를 생성해주세요:
대분류: [시스템 영역, 예: 스킬 시스템]
중분류: [주요 기능, 예: 아이템 장착]
소분류: [세부 기능, 예: 장비 세트 효과]
확인내용: [구체적인 테스트 내용, 예: 세트 아이템 장착 시 세트 효과가 캐릭터 스탯에 올바르게 적용되는지 확인]
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
        "대분류": "스킬 시스템",  # 기본값, 컨텍스트에 따라 변경 가능
        "중분류": "아이템 장착",  # 요청에 따라 변경된 기본값
        "소분류": "",
        "확인내용": "",
        "결과": "",
        "비고": ""
    }
    
    # 컨텍스트에서 중분류 추정
    if "장착" in context or "착용" in context:
        testcase["중분류"] = "아이템 장착"
    elif "스킬" in context and ("레벨" in context or "강화" in context):
        testcase["중분류"] = "스킬 강화"
    elif "스킬" in context and "해금" in context:
        testcase["중분류"] = "스킬 해금"
    elif "스킬" in context and "사용" in context:
        testcase["중분류"] = "스킬 사용"
    elif "세트" in context:
        testcase["중분류"] = "세트 효과"
    else:
        testcase["중분류"] = "아이템 장착"  # 기본값 유지
    
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

def split_into_sentences(text: str) -> List[str]:
    """
    텍스트를 문장 단위로 분리합니다.
    
    Args:
        text: 분할할 텍스트
        
    Returns:
        문장 리스트
    """
    # 문장 구분 패턴: 마침표, 물음표, 느낌표 뒤에 공백이 있는 경우
    # 한국어 문장 구분 고려
    sentence_delimiters = r'(?<=[.!?])\s+|(?<=。|\n|\r)'
    sentences = re.split(sentence_delimiters, text)
    
    # 빈 문장 제거
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def should_skip_sentence(sentence: str) -> bool:
    """
    테스트케이스 생성에서 제외할 문장인지 확인합니다.
    
    Args:
        sentence: 확인할 문장
        
    Returns:
        제외 여부 (True면 제외)
    """
    # 건너뛸 패턴
    skip_patterns = [
        r'^목차',
        r'^제\s*\d+\s*장',  # 제1장, 제 2 장 등
        r'^[0-9.]+\s*소개',
        r'^참고',
        r'^주의',
        r'^메모',
        r'^노트',
        r'^Table of Contents',
        r'^Index',
        r'^Figure',
        r'^표\s*\d+',  # 표 1, 표2 등
        r'^그림\s*\d+',  # 그림 1, 그림2 등
        r'^\s*$',  # 빈 줄
        r'^[A-Za-z0-9]+(\.[A-Za-z0-9]+)*\s*$',  # 단순 버전 표기
        r'^@',  # 이메일이나 참조
        r'^\d+\.\d+\.\d+$',  # 버전 번호만 있는 경우
        r'^\*\*',  # 마크다운 강조 텍스트
        r'^#+\s',  # 마크다운 헤더
        r'^-{3,}$', # 구분선
        r'^\[\d+\]$',  # 참조 번호
    ]
    
    # 문장이 짧으면 건너뜀 (최소 10자)
    if len(sentence) < 10:
        return True
    
    # 패턴에 해당하면 건너뜀
    for pattern in skip_patterns:
        if re.search(pattern, sentence):
            return True
    
    return False

def filter_and_extract_conditions_from_sentence(sentence: str) -> List[Dict[str, Any]]:
    """
    한 문장에서 조건을 추출하고 필터링합니다.
    
    Args:
        sentence: 분석할 문장
        
    Returns:
        조건 정보 목록
    """
    # 문장에서 조건 추출
    conditions = extract_conditional_statements(sentence)
    
    # 다음과 같은 경우 고려:
    # 1. 조건이 없어도 문장이 특정 키워드 포함하면 의미있을 수 있음
    if not conditions:
        important_keywords = [
            "버튼", "클릭", "팝업", "화면", "표시", "인터페이스", "UI", 
            "선택", "입력", "스왑", "드래그", "최대", "최소", "제한", 
            "오류", "에러", "예외", "네트워크", "연결", "배치", "상태",
            "아이템", "장착", "사용", "스킬", "캐릭터", "레벨", "경험치",
            "퀘스트", "미션", "전투", "공성전", "보상", "재화", "구매",
            "세트", "효과", "장비", "강화", "해금", "스탯", "능력치"
        ]
        
        # 중요 키워드가 있는지 확인
        has_keyword = any(keyword in sentence for keyword in important_keywords)
        
        # 중요 키워드가 없으면 빈 리스트 반환
        if not has_keyword:
            return []
        
        # 중요 키워드가 있으면 일반 조건으로 가정하고 진행
        # 기획 또는 기능 관련 일반 설명으로 처리
        conditions = [{
            "field": "GENERAL_FEATURE",
            "value": "DESCRIBED",
            "original": sentence
        }]
    
    return conditions

def determine_medium_category(context: str) -> str:
    """
    컨텍스트를 기반으로 중분류를 결정합니다.
    
    Args:
        context: 분석할 컨텍스트
        
    Returns:
        중분류명
    """
    # 컨텍스트에서 중분류 추정
    if "장착" in context or "착용" in context or "장비" in context:
        return "아이템 장착"
    elif "세트" in context and ("효과" in context or "보너스" in context):
        return "세트 효과"
    elif "스킬" in context and "강화" in context:
        return "스킬 강화"
    elif "스킬" in context and "해금" in context:
        return "스킬 해금"
    elif "스킬" in context and "사용" in context:
        return "스킬 사용"
    elif "능력치" in context or "스탯" in context:
        return "능력치 시스템"
    elif "장비" in context and "강화" in context:
        return "장비 강화"
    elif "장비" in context and ("변경" in context or "교체" in context):
        return "장비 변경"
    else:
        return "아이템 장착"  # 기본값

def generate_multiple_testcases_from_sentence(sentence: str, context: str) -> List[Dict[str, str]]:
    """
    한 문장에서 여러 테스트케이스를 생성합니다.
    
    Args:
        sentence: 분석할 문장
        context: 원본 컨텍스트 (주변 문장 포함)
        
    Returns:
        테스트케이스 목록
    """
    # 조건 추출
    conditions = filter_and_extract_conditions_from_sentence(sentence)
    
    # 조건이 없으면 빈 리스트 반환
    if not conditions:
        return []
    
    # 기본 테스트케이스 구조 생성
    base_testcase = {
        "대분류": "스킬 시스템",  # 기본값을 "스킬 시스템"으로 변경
        "중분류": "아이템 장착",  # 기본값을 "아이템 장착"으로 변경
        "소분류": "",
        "확인내용": "",
        "결과": "",
        "비고": ""
    }
    
    # 문맥 기반 대분류 설정 (기본값은 "스킬 시스템"으로 유지)
    if "퀘스트" in context or "미션" in context or "임무" in context:
        base_testcase["대분류"] = "퀘스트 시스템"
    elif "상점" in context or "구매" in context or "판매" in context:
        base_testcase["대분류"] = "상점 시스템"
    elif "전투" in context or "공격" in context or "방어" in context:
        base_testcase["대분류"] = "전투 시스템"
    
    # 문맥 기반 중분류 설정
    base_testcase["중분류"] = determine_medium_category(context)
    
    # 조건별 테스트케이스 생성
    testcases = []
    
    # 일반적인 설명 문장이면 (GENERAL_FEATURE)
    if len(conditions) == 1 and conditions[0]["field"] == "GENERAL_FEATURE":
        # 일반 기능 설명에서 테스트케이스 생성
        testcase = base_testcase.copy()
        
        # 문맥에 따라 소분류 변경
        if "세트" in sentence:
            testcase["소분류"] = "세트 효과"
        elif "능력치" in sentence or "스탯" in sentence:
            testcase["소분류"] = "능력치 적용"
        elif "강화" in sentence:
            testcase["소분류"] = "장비 강화"
        elif "레벨" in sentence:
            testcase["소분류"] = "레벨 요구사항"
        else:
            testcase["소분류"] = "일반 기능"
        
        # UI 및 상호작용 패턴 확인
        check_content = ""
        for pattern, check in UI_INTERACTION_PATTERNS.items():
            if re.search(pattern, sentence):
                check_content = check
                break
        
        # 예외 상황 패턴 확인
        if not check_content:
            for pattern, check in EXCEPTION_PATTERNS.items():
                if re.search(pattern, sentence):
                    check_content = check
                    break
        
        # 패턴이 없으면 일반 확인 내용
        if not check_content:
            # 아이템 장착 관련 기본 테스트 케이스 추가
            if base_testcase["중분류"] == "아이템 장착":
                check_content = "아이템 장착 시 캐릭터 외형 및 능력치가 올바르게 변경되는지 확인"
            else:
                check_content = f"'{sentence}' 기능이 기획서 내용대로 동작하는지 확인"
        
        testcase["확인내용"] = check_content
        testcase["비고"] = "기획서 일반 설명 기반"
        testcases.append(testcase)
    else:
        # 조건별 테스트케이스 생성
        for condition in conditions:
            testcase = base_testcase.copy()
            field = condition["field"]
            value = condition["value"]
            
            # 소분류 설정
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
            else:
                # 알려진 룰이 없는 조건은 일반적인 확인내용 생성
                check_content = f"{field}가 {value}인 경우 올바르게 동작하는지 확인"
            
            testcase["확인내용"] = check_content
            testcase["비고"] = f"조건: {condition['original']}"
            testcases.append(testcase)
    
    return testcases

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
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "일반",
                "확인내용": "아이템 장착 시 캐릭터 외형 및 능력치가 올바르게 변경되는지 확인",
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
    
    # 문장 분리 및 테스트케이스 생성
    testcases = []
    sentences = split_into_sentences(context)
    
    for sentence in sentences:
        if should_skip_sentence(sentence):
            continue
        
        # 문장별 테스트케이스 생성
        sentence_testcases = generate_multiple_testcases_from_sentence(sentence, context)
        testcases.extend(sentence_testcases)
    
    # 결과가 없으면 기본 테스트케이스 추가
    if not testcases:
        # 기본 테스트케이스 목록 생성 - 스킬 시스템과 아이템 장착 관련 테스트케이스
        default_testcases = [
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "장착 기능",
                "확인내용": "아이템 장착 시 캐릭터 외형이 올바르게 변경되는지 확인",
                "결과": "",
                "비고": "기본 테스트케이스"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "능력치 적용",
                "확인내용": "아이템 장착 시 캐릭터 능력치가 올바르게 증가하는지 확인",
                "결과": "",
                "비고": "기본 테스트케이스"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "장착 제한",
                "확인내용": "요구 레벨/클래스 미달 시 아이템 장착이 제한되는지 확인",
                "결과": "",
                "비고": "기본 테스트케이스"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "UI 표시",
                "확인내용": "장비창에서 장착된 아이템이 하이라이트 표시되는지 확인",
                "결과": "",
                "비고": "기본 테스트케이스"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "세트 효과",
                "확인내용": "동일 세트 아이템 여러 개 장착 시 세트 효과가 활성화되는지 확인",
                "결과": "",
                "비고": "기본 테스트케이스"
            }
        ]
        testcases.extend(default_testcases)
    
    return testcases

def generate_testcases(vector_db, document_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    전체 문서를 기반으로 테스트케이스 생성
    
    Args:
        vector_db: FAISS 벡터 DB 정보
        document_chunks: 문서 청크 목록
        
    Returns:
        생성된 테스트케이스 목록
    """
    testcases = []
    
    # 청크별로 처리
    for chunk in document_chunks:
        # 청크 텍스트 가져오기
        context = chunk['text']
        
        # 문장 단위로 분리
        sentences = split_into_sentences(context)
        
        # 문장별로 테스트케이스 생성
        for sentence in sentences:
            # 건너뛸 문장 확인
            if should_skip_sentence(sentence):
                continue
            
            # 문장에서 테스트케이스 생성
            sentence_testcases = generate_multiple_testcases_from_sentence(sentence, context)
            
            # 생성된 테스트케이스가 있으면 추가
            testcases.extend(sentence_testcases)
    
    # 문서를 기반으로 한 테스트케이스가 없으면 기본 테스트케이스 추가
    if not testcases:
        # 스킬 시스템과 아이템 장착 관련 기본 테스트케이스 추가
        comprehensive_testcases = [
            # 장비 장착 기본 기능
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "장착 기능",
                "확인내용": "아이템을 장착 슬롯에 드래그하여 장착이 정상적으로 되는지 확인",
                "결과": "",
                "비고": "필수 테스트 케이스"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "해제 기능",
                "확인내용": "장착된 아이템을 클릭하여 해제가 정상적으로 되는지 확인",
                "결과": "",
                "비고": "필수 테스트 케이스"
            },
            
            # 시각적 피드백
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "캐릭터 외형",
                "확인내용": "장비 장착 시 캐릭터 외형이 해당 장비 착용 모습으로 변경되는지 확인",
                "결과": "",
                "비고": "시각적 피드백"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "UI 표시",
                "확인내용": "장착 중인 아이템이 캐릭터 정보창과 장비창에서 하이라이트되는지 확인",
                "결과": "",
                "비고": "UI 피드백"
            },
            
            # 능력치 반영
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "공격력 증가",
                "확인내용": "공격력 증가 효과가 있는 아이템 장착 시 캐릭터 공격력이 정확히 증가하는지 확인",
                "결과": "",
                "비고": "스탯 반영"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "방어력 증가",
                "확인내용": "방어력 증가 효과가 있는 아이템 장착 시 캐릭터 방어력이 정확히 증가하는지 확인",
                "결과": "",
                "비고": "스탯 반영"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "체력 증가",
                "확인내용": "체력 증가 효과가 있는 아이템 장착 시 캐릭터 최대 체력이 정확히 증가하는지 확인",
                "결과": "",
                "비고": "스탯 반영"
            },
            
            # 세트 효과
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "세트 활성화",
                "확인내용": "같은 세트의 아이템 2개를 장착했을 때 2세트 효과가 활성화되는지 확인",
                "결과": "",
                "비고": "세트 효과"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "세트 UI",
                "확인내용": "세트 효과 활성화 시 세트 효과 UI에 활성화된 세트가 표시되는지 확인",
                "결과": "",
                "비고": "세트 효과 UI"
            },
            
            # 장착 제한
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "레벨 제한",
                "확인내용": "요구 레벨보다 낮은 레벨의 캐릭터가 아이템 장착 시 실패 메시지가 표시되는지 확인",
                "결과": "",
                "비고": "장착 제한"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "클래스 제한",
                "확인내용": "다른 클래스 전용 아이템 장착 시 실패 메시지가 표시되는지 확인",
                "결과": "",
                "비고": "장착 제한"
            },
            
            # 장비 교체
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "장비 교체",
                "확인내용": "이미 장착된 슬롯에 새 아이템 장착 시 기존 아이템이 인벤토리로 이동하는지 확인",
                "결과": "",
                "비고": "장비 교체"
            },
            
            # 스킬 관련
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "스킬 효과",
                "확인내용": "특정 스킬 강화 효과가 있는 아이템 장착 시 해당 스킬 데미지가 증가하는지 확인",
                "결과": "",
                "비고": "스킬 연동"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "스킬 해금",
                "확인내용": "특정 스킬 해금 효과가 있는 아이템 장착 시 해당 스킬이 사용 가능해지는지 확인",
                "결과": "",
                "비고": "스킬 연동"
            },
            
            # 특수 효과
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "특수 효과",
                "확인내용": "특수 효과(독데미지 감소, 스턴 저항 등)가 있는 아이템 장착 시 해당 효과가 적용되는지 확인",
                "결과": "",
                "비고": "특수 효과"
            },
            
            # 내구도
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "내구도",
                "확인내용": "내구도가 있는 아이템을 사용할 때마다 내구도가 감소하는지 확인",
                "결과": "",
                "비고": "내구도 시스템"
            },
            {
                "대분류": "스킬 시스템",
                "중분류": "아이템 장착",
                "소분류": "내구도 UI",
                "확인내용": "낮은 내구도 아이템은 UI에서 경고 표시가 나타나는지 확인",
                "결과": "",
                "비고": "내구도 시스템"
            }
        ]
        testcases.extend(comprehensive_testcases)
    
    return testcases