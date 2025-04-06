"""
RAG 엔진 모듈: 벡터 DB에서 관련 정보를 검색하고 테스트케이스 생성
"""

from typing import List, Dict, Any
import numpy as np

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
플랫폼: [지원 플랫폼, 예: AD, iOS, PC]
비고: [추가 참고사항]

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
    
    def generate_testcase(self, query: str, context: str) -> Dict[str, str]:
        """
        컨텍스트를 기반으로 테스트케이스 생성
        
        Args:
            query: 사용자 쿼리
            context: 검색된 관련 컨텍스트
            
        Returns:
            생성된 테스트케이스
        """
        # 여기서는 실제 LLM 구현이 없으므로 템플릿 예시만 반환
        # 실제 구현에서는 Ollama나 다른 로컬 LLM을 사용
        
        # 예시 테스트케이스 - 실제 구현에서는 LLM 응답으로 대체
        testcase = {
            "대분류": "아이템 시스템",
            "중분류": "아이템 능력치",
            "소분류": "고유 능력치",
            "확인내용": "아이템 장착 시 고유 능력치가 캐릭터에 적용되는지 확인",
            "플랫폼": "AD, iOS, PC",
            "비고": "장착 가능한 아이템만 테스트"
        }
        
        return testcase

def process_rag(vector_db, user_query: str) -> List[Dict[str, str]]:
    """
    RAG 프로세스 실행 함수
    
    Args:
        vector_db: FAISS 벡터 DB 정보
        user_query: 사용자 쿼리
        
    Returns:
        생성된 테스트케이스 목록
    """
    rag_engine = RAGEngine(vector_db)
    
    # 관련 청크 검색
    relevant_chunks = rag_engine.retrieve_relevant_chunks(user_query)
    
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
    
    # 간단한 예시 - 실제 구현에서는 더 복잡한 로직 필요
    for i, chunk in enumerate(document_chunks[:5]):  # 예시로 처음 5개 청크만 처리
        # 각 청크를 쿼리로 사용
        query = f"이 내용에 대한 테스트케이스를 생성해주세요: {chunk['text'][:100]}..."
        
        # 관련 청크 검색
        relevant_chunks = rag_engine.retrieve_relevant_chunks(query)
        
        # 컨텍스트 통합
        context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
        
        # 테스트케이스 생성
        testcase = rag_engine.generate_testcase(query, context)
        testcases.append(testcase)
    
    return testcases