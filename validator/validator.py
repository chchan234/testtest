"""
테스트케이스 검증 모듈: 생성된 테스트케이스의 품질 및 정확성 검증
"""

from typing import List, Dict, Any
import re

# 검증 프롬프트 템플릿
VALIDATION_PROMPT = """
당신은 테스트케이스 검증 전문가입니다.
생성된 테스트케이스가 원본 기획서 내용을 정확히 반영하는지 검증해주세요.

원본 기획서 내용:
{original_content}

생성된 테스트케이스:
대분류: {major}
중분류: {medium}
소분류: {minor}
확인내용: {content}
결과: {result}
JIRA: {jira}
AD: {ad}
iOS: {ios}
PC: {pc}
비고: {note}

다음 항목을 기준으로 테스트케이스를 평가해주세요:
1. 정확성: 테스트케이스가 기획서 내용을 정확히 반영하는가?
2. 완전성: 기획서의 주요 요구사항이 누락 없이 모두 포함되었는가?
3. 명확성: 테스트케이스가 명확하게 작성되었는가?
4. 플랫폼 적합성: 지정된 플랫폼(AD, iOS, PC)에 적합한 내용인가?

검증 결과:
- 정확성 점수(1-10):
- 완전성 점수(1-10):
- 명확성 점수(1-10):
- 플랫폼 적합성 점수(1-10):
- 총점:
- 개선 제안:
"""

class TestcaseValidator:
    """테스트케이스 검증 클래스"""
    
    def __init__(self):
        """검증기 초기화"""
        pass
    
    def validate_testcase(self, testcase: Dict[str, str], original_content: str) -> Dict[str, Any]:
        """
        테스트케이스 검증
        
        Args:
            testcase: 검증할 테스트케이스
            original_content: 원본 기획서 내용
            
        Returns:
            검증 결과
        """
        # 여기서는 실제 LLM 구현이 없으므로 예시 검증 결과만 반환
        # 실제 구현에서는 Ollama나 다른 로컬 LLM을 사용
        
        # 테스트케이스 정보 추출
        major = testcase.get("대분류", "")
        medium = testcase.get("중분류", "")
        minor = testcase.get("소분류", "")
        content = testcase.get("확인내용", "")
        result = testcase.get("결과", "")
        jira = testcase.get("JIRA", "")
        ad = testcase.get("AD", "")
        ios = testcase.get("iOS", "")
        pc = testcase.get("PC", "")
        note = testcase.get("비고", "")
        
        # 예시 검증 결과 - 실제 구현에서는 LLM 응답으로 대체
        validation_result = {
            "정확성": 8,
            "완전성": 7,
            "명확성": 9,
            "플랫폼_적합성": 8,
            "총점": 8.0,
            "개선_제안": "소분류에 좀더 구체적인 내용을 추가하면 좋겠습니다.",
            "통과_여부": True
        }
        
        # 플랫폼별 검증 결과 점수 조정
        # 만약 플랫폼 정보가 있다면 플랫폼 적합성 점수 추가 반영
        if ad or ios or pc:
            validation_result["플랫폼_적합성"] = min(10, validation_result["플랫폼_적합성"] + 1)
        
        # 총점 재계산
        validation_result["총점"] = (
            validation_result["정확성"] + 
            validation_result["완전성"] + 
            validation_result["명확성"] + 
            validation_result["플랫폼_적합성"]
        ) / 4.0
        
        return validation_result

def validate_testcases(testcases: List[Dict[str, str]], original_content: str) -> List[Dict[str, Any]]:
    """
    테스트케이스 목록 검증
    
    Args:
        testcases: 검증할 테스트케이스 목록
        original_content: 원본 기획서 내용
        
    Returns:
        각 테스트케이스의 검증 결과
    """
    validator = TestcaseValidator()
    validation_results = []
    
    for testcase in testcases:
        # 테스트케이스 검증
        result = validator.validate_testcase(testcase, original_content)
        
        # 결과에 테스트케이스 정보 추가
        result["testcase"] = testcase
        
        validation_results.append(result)
    
    return validation_results