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

# 좋은 확인내용 패턴 (QA 관점의 테스트 케이스)
GOOD_CONTENT_PATTERNS = [
    r"버튼이.*노출",
    r"버튼이.*비활성화",
    r"표시.*확인",
    r"정상.*동작",
    r"적용.*확인",
    r"오류.*메시지",
    r"알림.*표시",
    r"UI.*표시",
    r"경고.*노출",
    r"팝업.*표시"
]

# 미흡한 확인내용 패턴 (단순 기술적 조건 확인)
POOR_CONTENT_PATTERNS = [
    r"이.*동작",
    r"가.*동작",
    r".*값.*확인",
    r"TRUE|FALSE",
    r"설정.*확인",
    r"^조건.*확인$"
]

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
        
        # 점수 초기화
        accuracy = 0  # 정확성
        completeness = 0  # 완전성
        clarity = 0  # 명확성
        platform_relevance = 0  # 플랫폼 적합성
        
        # 1. 정확성 평가
        # - 원본 내용에 관련 키워드가 포함되어 있는지 확인
        if minor and re.search(minor, original_content, re.IGNORECASE):
            accuracy += 5  # 소분류가 원본에 포함됨
        elif medium and re.search(medium, original_content, re.IGNORECASE):
            accuracy += 3  # 중분류가 원본에 포함됨
        
        # - 확인내용이 구체적인지 확인
        if content:
            is_qa_perspective = False
            for pattern in GOOD_CONTENT_PATTERNS:
                if re.search(pattern, content):
                    is_qa_perspective = True
                    break
            
            if is_qa_perspective:
                accuracy += 5  # QA 관점의 구체적인 확인내용
            else:
                for pattern in POOR_CONTENT_PATTERNS:
                    if re.search(pattern, content):
                        accuracy += 2  # 단순 조건 확인
                        break
                else:
                    accuracy += 3  # 그 외 경우
        
        # 2. 완전성 평가
        # - 필수 필드가 채워져 있는지 확인
        if major:
            completeness += 2
        if medium:
            completeness += 2
        if minor:
            completeness += 2
        if content:
            completeness += 4
        
        # 3. 명확성 평가
        # - 확인내용의 품질 평가
        if content:
            # 확인내용이 구체적인지 (단어 수, 명확한 설명 포함 여부)
            if len(content.split()) >= 6:
                clarity += 5  # 상세한 설명
            elif len(content.split()) >= 4:
                clarity += 3  # 적당한 설명
            else:
                clarity += 1  # 간단한 설명
            
            # 특정 동작이나 검증 방법이 명시되어 있는지
            if "확인" in content or "검증" in content or "테스트" in content:
                clarity += 3
            
            # UI 또는 사용자 상호작용을 포함하는지
            if "UI" in content or "버튼" in content or "표시" in content or "화면" in content:
                clarity += 2
        
        # 4. 플랫폼 적합성 평가
        # - 플랫폼 정보 지정 여부
        platform_count = sum(1 for p in [ad, ios, pc] if p)
        if platform_count == 3:
            platform_relevance += 5  # 모든 플랫폼 지정
        elif platform_count > 0:
            platform_relevance += 3  # 일부 플랫폼 지정
        
        # - 플랫폼별 특성 고려 여부
        if "버튼" in content or "UI" in content or "화면" in content:
            platform_relevance += 3  # UI 관련 내용
        if "네트워크" in content or "연결" in content:
            platform_relevance += 2  # 네트워크 관련 내용
        
        # 점수 정규화 (1-10 범위로)
        accuracy = min(10, max(1, accuracy))
        completeness = min(10, max(1, completeness))
        clarity = min(10, max(1, clarity))
        platform_relevance = min(10, max(1, platform_relevance))
        
        # 총점 계산
        total_score = (accuracy + completeness + clarity + platform_relevance) / 4.0
        
        # 개선 제안 생성
        improvement_suggestions = []
        if accuracy < 7:
            improvement_suggestions.append("기획서 내용을 더 정확히 반영할 필요가 있습니다.")
        if completeness < 7:
            improvement_suggestions.append("테스트케이스에 더 많은 정보를 포함해야 합니다.")
        if clarity < 7:
            improvement_suggestions.append("확인내용을 더 명확하고 구체적으로 작성해야 합니다.")
        if platform_relevance < 7:
            improvement_suggestions.append("플랫폼별 특성을 더 고려한 테스트케이스가 필요합니다.")
        
        if not improvement_suggestions:
            improvement_suggestions.append("테스트케이스가 잘 작성되었습니다.")
        
        # 최종 검증 결과
        validation_result = {
            "정확성": int(accuracy),
            "완전성": int(completeness),
            "명확성": int(clarity),
            "플랫폼_적합성": int(platform_relevance),
            "총점": round(total_score, 1),
            "개선_제안": " ".join(improvement_suggestions),
            "통과_여부": total_score >= 7.0
        }
        
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