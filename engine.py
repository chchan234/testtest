"""
RAG 엔진 모듈: 벡터 DB에서 관련 정보를 검색하고 테스트케이스 생성
"""

from typing import List, Dict, Any
import numpy as np
import re

from embedding.embedder import search_similar

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
확인내용: [구체적인 테스트 내용]
결과: [테스트 결과, 예: "통과", "실패" 또는 비워둠]
JIRA: [JIRA 티켓 번호 또는 비워둠]
AD: [AD 플랫폼 테스트 결과, 예: PASS, FAIL, BLOCKED 또는 비워둠]
iOS: [iOS 플랫폼 테스트 결과, 예: PASS, FAIL, BLOCKED 또는 비워둠]
PC: [PC 플랫폼 테스트 결과, 예: PASS, FAIL, BLOCKED 또는 비워둠]
비고: [추가 참고사항]

기획서의 각 문장이나 중요 내용마다 최소 하나 이상의 테스트케이스를 생성해주세요.
계층 구조를 유지하고, 관련 항목끼리 그룹화하여 작성해주세요.

테스트케이스:
"""

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
    
    def generate_testcase(self, query: str, context: str) -> List[Dict[str, str]]:
        """
        컨텍스트를 기반으로 테스트케이스 생성
        
        Args:
            query: 사용자 쿼리
            context: 검색된 관련 컨텍스트
            
        Returns:
            생성된 테스트케이스 목록
        """
        # 여기서는 실제 LLM 구현이 없으므로 템플릿 예시만 반환
        # 실제 구현에서는 Ollama나 다른 로컬 LLM을 사용
        
        # 문장 분리 (간단한 구현으로, 실제로는 더 정교한 분석 필요)
        sentences = self._split_into_sentences(context)
        testcases = []
        
        # 문서 전체에서 대분류, 중분류, 소분류 정보 추출 시도
        major_categories = self._extract_document_structure(context)
        
        current_major = "시스템"
        current_medium = "기능"
        current_minor = "세부 기능"
        
        if major_categories:
            # 추출된 구조가 있다면 첫 번째 카테고리 사용
            current_major = major_categories[0].get('major', current_major)
            current_medium = major_categories[0].get('medium', current_medium)
            current_minor = major_categories[0].get('minor', current_minor)
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip() or len(sentence.strip()) < 10:
                continue  # 짧은 문장 또는 빈 문장 제외
                
            # 새로운 카테고리 감지
            if i > 0 and len(sentence.strip()) < 50 and any(keyword in sentence.lower() for keyword in ['시스템', '기능', '모듈', '설정']):
                # 구조 업데이트
                for category in major_categories:
                    for key_phrase in [category.get('major', ''), category.get('medium', ''), category.get('minor', '')]:
                        if key_phrase and key_phrase in sentence:
                            current_major = category.get('major', current_major)
                            current_medium = category.get('medium', current_medium)
                            current_minor = category.get('minor', current_minor)
                            break
            
            # 분류 정보 추정 (실제 구현에서는 더 정교한 로직 필요)
            major, medium, minor = self._extract_categories(sentence, current_major, current_medium, current_minor)
            
            # 만약 새로운 분류 정보가 추출되었다면 현재 컨텍스트 업데이트
            if major != current_major and len(major.strip()) > 2:
                current_major = major
            if medium != current_medium and len(medium.strip()) > 2:
                current_medium = medium
            if minor != current_minor and len(minor.strip()) > 2:
                current_minor = minor
            
            # 테스트 케이스 생성
            testcase = {
                "대분류": current_major,
                "중분류": current_medium,
                "소분류": current_minor,
                "확인내용": self._create_test_content(sentence),
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": ""
            }
            testcases.append(testcase)
        
        # 적어도 하나의 테스트케이스는 반환
        if not testcases:
            testcases = [{
                "대분류": current_major,
                "중분류": current_medium,
                "소분류": current_minor,
                "확인내용": "기획서 내용에 대한 기능 작동 여부 확인",
                "결과": "",
                "JIRA": "",
                "AD": "",
                "iOS": "",
                "PC": "",
                "비고": ""
            }]
        
        return testcases
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        텍스트를 문장 단위로 분리
        """
        # 문장 끝 패턴 (마침표, 느낌표, 물음표 등) 으로 분리
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # 번호 목록 형태(1., 2. 등)도 문장으로 간주
        numbered_sentences = []
        for sentence in sentences:
            # 번호 목록 항목 분리
            numbered_parts = re.split(r'(?<=\d\.)\s+', sentence)
            numbered_sentences.extend([part.strip() for part in numbered_parts if part.strip()])
        
        # 불필요한 공백 제거
        clean_sentences = [s.strip() for s in numbered_sentences if s.strip()]
        return clean_sentences
    
    def _extract_document_structure(self, text: str) -> List[Dict[str, str]]:
        """
        문서에서 구조적 정보(대분류, 중분류, 소분류) 추출
        """
        # 정규식으로 구조를 찾는 패턴
        structure = []
        
        # 제목이나 헤딩으로 보이는 라인 찾기
        heading_lines = re.findall(r'^.*?[:：\.].*$', text, re.MULTILINE)
        
        for line in heading_lines:
            parts = re.split(r'[:：\.]', line, 1)
            if len(parts) > 1 and len(parts[0].strip()) < 50:  # 제목은 보통 짧음
                # 계층 구조 추출 시도 (대>중>소 등의 패턴)
                hierarchy = re.split(r'[>-]', parts[0])
                if len(hierarchy) >= 3:
                    structure.append({
                        'major': hierarchy[0].strip(),
                        'medium': hierarchy[1].strip(),
                        'minor': hierarchy[2].strip()
                    })
                elif len(hierarchy) == 2:
                    structure.append({
                        'major': hierarchy[0].strip(),
                        'medium': hierarchy[1].strip(),
                        'minor': '기본 기능'
                    })
                else:
                    # 단일 수준 제목
                    title = parts[0].strip()
                    # 제목에 '시스템'이 있으면 대분류로
                    if '시스템' in title:
                        structure.append({
                            'major': title,
                            'medium': '기능',
                            'minor': '세부 기능'
                        })
                    else:
                        structure.append({
                            'major': '시스템',
                            'medium': title,
                            'minor': '세부 기능'
                        })
        
        return structure
    
    def _extract_categories(self, sentence: str, default_major: str, default_medium: str, default_minor: str) -> tuple:
        """
        문장에서 분류 정보 추출 시도
        """
        # 실제 구현에서는 더 정교한 분석 로직 필요
        # 여기서는 단순화된 구현만 제공
        major = default_major
        medium = default_medium
        minor = default_minor
        
        # '시스템' 패턴이 있으면 대분류 후보로 판단
        if re.search(r'(시스템|기능|모듈)', sentence):
            major_candidates = re.findall(r'([가-힣A-Za-z]+\s*(시스템|기능|모듈))', sentence)
            if major_candidates:
                major = major_candidates[0][0]
        
        # 중분류, 소분류 추출 시도 - 제한된 구현
        if ":" in sentence:
            parts = sentence.split(":", 1)
            if len(parts[0].strip()) < 30:  # 짧은 레이블이면 분류 후보로 간주
                if '>' in parts[0] or '-' in parts[0]:
                    category_parts = re.split(r'[>-]', parts[0])
                    if len(category_parts) >= 2:
                        medium = category_parts[0].strip()
                        minor = category_parts[1].strip()
                else:
                    medium = parts[0].strip()
        
        return major, medium, minor
    
    def _create_test_content(self, sentence: str) -> str:
        """
        문장을 테스트 내용으로 변환
        """
        # 설명문 패턴 제거
        sentence = re.sub(r'^[\s\-•*]+', '', sentence).strip()
        
        # 질문형으로 변환
        if not re.search(r'[?？]$', sentence):
            # 이미 테스트 내용인지 확인
            if re.search(r'확인$|테스트$|체크$', sentence):
                content = sentence
            # 의문문이 아니면 확인 내용으로 변환
            elif re.search(r'여부|가능|동작|작동|확인|체크', sentence):
                content = f"{sentence} 정상 작동 확인"
            else:
                content = f"{sentence}에 대한 기능 동작 확인"
        else:
            content = sentence
        
        return content

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
    testcases = rag_engine.generate_testcase(user_query, context)
    
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
    rag_engine = RAGEngine(vector_db)
    all_testcases = []
    
    # 각 청크에 대해 처리
    for chunk in document_chunks:
        # 각 청크를 쿼리로 사용
        query = f"이 내용에 대한 테스트케이스를 생성해주세요: {chunk['text'][:100]}..."
        
        # 관련 청크 검색 (자기 자신 포함)
        relevant_chunks = rag_engine.retrieve_relevant_chunks(query)
        
        # 컨텍스트 통합
        context = "\n\n".join([c['text'] for c in relevant_chunks])
        
        # 테스트케이스 생성
        testcases = rag_engine.generate_testcase(query, context)
        all_testcases.extend(testcases)
    
    # 중복 제거 (확인내용 기준)
    unique_testcases = []
    seen_contents = set()
    
    for tc in all_testcases:
        content = tc["확인내용"]
        if content not in seen_contents:
            seen_contents.add(content)
            unique_testcases.append(tc)
    
    return unique_testcases